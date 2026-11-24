"""ELF helpers, Unicorn state cloning, and branch-path analysis."""

from __future__ import annotations

import json
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path

from capstone import CS_ARCH_X86, CS_GRP_JUMP, CS_MODE_64, Cs
from capstone.x86 import X86_OP_IMM

from page_table import (
    MACHINE_PAGE_TABLE,
    PAGE_SIZE,
    PageTable,
    elf_flags_to_unicorn,
    map_page_table,
)
from unicorn import (
    Uc,
    UC_ARCH_X86,
    UC_HOOK_CODE,
    UC_HOOK_MEM_READ,
    UC_HOOK_MEM_WRITE,
    UC_HOOK_MEM_INVALID,
    UC_MODE_64,
    UC_PROT_ALL,
    UC_MEM_WRITE,
    UcError,
)
PAGE = PAGE_SIZE
KERNEL_BUF_ADDR = 0xC0004000


LEAK_START = 0x404000
LEAK_END = 0x405000  

class LabError(RuntimeError):
    """An input, build, or emulation setup error."""


@dataclass
class ElfImage:
    entry: int
    # (virtual address, memory size, file bytes, ELF p_flags)
    loads: list[tuple[int, int, bytes, int]]


def align_down(value: int, alignment: int) -> int:
    return value & ~(alignment - 1)


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def read_elf64(path: Path) -> ElfImage:
    """Read PT_LOAD segments, preserving their ELF permission flags."""
    data = path.read_bytes()
    if len(data) < 64 or data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
        raise LabError("expected a little-endian ELF64 executable")

    header = struct.unpack_from("<16sHHIQQQIHHHHHH", data, 0)
    entry, phoff, phentsize, phnum = header[4], header[5], header[9], header[10]
    loads: list[tuple[int, int, bytes, int]] = []
    for index in range(phnum):
        offset = phoff + index * phentsize
        p_type, flags, p_offset, p_vaddr, _paddr, p_filesz, p_memsz, _align = (
            struct.unpack_from("<IIQQQQQQ", data, offset)
        )
        if p_type == 1:  # PT_LOAD
            file_bytes = data[p_offset : p_offset + p_filesz]
            loads.append((p_vaddr, p_memsz, file_bytes, flags))

    if not loads:
        raise LabError("ELF file has no loadable segments")
    return ElfImage(entry, loads)


def get_symbols(elf_path: Path, nm: str) -> dict[str, tuple[int, int]]:
    try:
        output = subprocess.check_output(
            [nm, "-S", "--defined-only", str(elf_path)], text=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LabError(f"could not read ELF symbols with {nm!r}: {exc}") from exc

    symbols: dict[str, tuple[int, int]] = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 4:
            try:
                symbols[fields[-1]] = (int(fields[0], 16), int(fields[1], 16))
            except ValueError:
                continue

    for name in ("victim", "user_buf", "kernel_buf"):
        if name not in symbols:
            raise LabError(f"ELF is missing symbol {name!r}; compile the supplied victim.c")
    return symbols


def compile_victim(
    source: Path, cc: str, nm: str, build_dir: Path
) -> tuple[Path, dict[str, tuple[int, int]]]:
    """Build and save the reusable assembly, ELF, and symbol metadata."""
    build_dir.mkdir(parents=True, exist_ok=True)
    elf_path = build_dir / "victim.elf"
    assembly_out = build_dir / "victim.s"
    symbols_out = build_dir / "victim_symbols.json"

    common = [
        cc,
        "-O0",
        "-fno-pie",
        "-fno-stack-protector",
        "-fno-inline",
        "-fcf-protection=none",
        "-mcmodel=large",
    ]
    asm_command = common + ["-S", "-masm=intel", str(source), "-o", str(assembly_out)]
    link_command = common + [
        "-nostdlib",
        "-no-pie",
        "-Wl,-e,victim",
        "-Wl,--build-id=none",
        f"-Wl,--section-start=.kernel_buf={KERNEL_BUF_ADDR:#x}",
        str(source),
        "-o",
        str(elf_path),
    ]

    try:
        subprocess.run(asm_command, check=True, capture_output=True, text=True)
        subprocess.run(link_command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise LabError(f"compiler {cc!r} was not found") from exc
    except subprocess.CalledProcessError as exc:
        raise LabError(f"compilation failed:\n{exc.stderr}") from exc

    symbols = get_symbols(elf_path, nm)
    if symbols["kernel_buf"][0] != KERNEL_BUF_ADDR:
        raise LabError(
            f"kernel_buf linked at {symbols['kernel_buf'][0]:#x}, expected "
            f"{KERNEL_BUF_ADDR:#x}; ensure victim.c places it in .kernel_buf"
        )

    symbols_out.write_text(
        json.dumps(
            {
                name: {"address": address, "size": size}
                for name, (address, size) in symbols.items()
            },
            indent=2,
        )
        + "\n"
    )
    return elf_path, symbols


def load_cached_symbols(path: Path) -> dict[str, tuple[int, int]]:
    try:
        raw = json.loads(path.read_text())
        symbols = {
            name: (int(info["address"]), int(info["size"]))
            for name, info in raw.items()
        }
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise LabError(f"could not read cached symbols from {path}: {exc}") from exc

    for name in ("victim", "user_buf", "kernel_buf"):
        if name not in symbols:
            raise LabError(f"cached symbol file is missing {name!r}; run with --build")
    return symbols


def map_image(uc: Uc, image: ElfImage) -> PageTable:
    """Create software PTEs for PT_LOAD segments and apply them to Unicorn."""
    page_table = PageTable()

    for vaddr, mem_size, file_bytes, flags in image.loads:
        if mem_size <= 0:
            continue

        permissions = elf_flags_to_unicorn(flags)
        first_page = align_down(vaddr, PAGE)
        limit = align_up(vaddr + mem_size, PAGE)
        for page in range(first_page, limit, PAGE):
            page_table.add_page(page, permissions=permissions)

        # Page entries are zero-initialized; the remainder of each segment is BSS.
        for offset, byte in enumerate(file_bytes):
            address = vaddr + offset
            entry = page_table.lookup(address)
            assert entry is not None
            entry.contents[address - page_table.page_base(address)] = byte

    map_page_table(uc, page_table)
    return page_table


def find_branch_starts_and_merge(
    uc: Uc,
    branch_address: int,
    function_address: int,
    function_size: int,
) -> tuple[int, int, int]:
    """Return taken start, fall-through start, and nearest common merge PC."""
    code = bytes(uc.mem_read(function_address, function_size))
    disasm = Cs(CS_ARCH_X86, CS_MODE_64)
    disasm.detail = True
    instructions = list(disasm.disasm(code, function_address))
    by_address = {insn.address: insn for insn in instructions}

    branch = by_address.get(branch_address)
    if branch is None or not branch.group(CS_GRP_JUMP):
        raise LabError(f"no branch instruction found at {branch_address:#x}")
    if branch.mnemonic.lower() in ("jmp", "ljmp"):
        raise LabError("expected a conditional branch, got an unconditional jump")
    if not branch.operands or branch.operands[0].type != X86_OP_IMM:
        raise LabError("branch target is not a direct immediate address")

    taken_start = branch.operands[0].imm
    fallthrough_start = branch.address + branch.size

    def successors(insn) -> list[int]:
        next_address = insn.address + insn.size
        mnemonic = insn.mnemonic.lower()
        if mnemonic in ("ret", "retf", "iret", "iretd", "iretq", "ud2", "hlt"):
            return []
        if insn.group(CS_GRP_JUMP):
            if not insn.operands or insn.operands[0].type != X86_OP_IMM:
                return [next_address] if next_address in by_address else []
            target = insn.operands[0].imm
            if mnemonic in ("jmp", "ljmp"):
                return [target] if target in by_address else []
            return [addr for addr in (target, next_address) if addr in by_address]
        # Calls are treated as returning to their next instruction.
        return [next_address] if next_address in by_address else []

    def reachable_distances(start: int) -> dict[int, int]:
        if start not in by_address:
            return {}
        distances = {start: 0}
        worklist = [start]
        index = 0
        while index < len(worklist):
            current = worklist[index]
            index += 1
            for destination in successors(by_address[current]):
                if destination not in distances:
                    distances[destination] = distances[current] + 1
                    worklist.append(destination)
        return distances

    taken_distances = reachable_distances(taken_start)
    fallthrough_distances = reachable_distances(fallthrough_start)
    common = taken_distances.keys() & fallthrough_distances.keys()
    if not common:
        raise LabError(
            f"no merge found for branch at {branch_address:#x} within function range "
            f"{function_address:#x}..{function_address + function_size:#x}"
        )

    merge_address = min(
        common,
        key=lambda address: (
            max(taken_distances[address], fallthrough_distances[address]),
            taken_distances[address] + fallthrough_distances[address],
            address,
        ),
    )
    return taken_start, fallthrough_start, merge_address


def clone_uc_state(source: Uc) -> Uc:
    """Clone mapped memory and CPU context; hooks must be reinstalled separately."""
    child = Uc(UC_ARCH_X86, UC_MODE_64)
    source_page_table = MACHINE_PAGE_TABLE[id(source)]
    child_page_table = source_page_table.clone_current(source)
    map_page_table(child, child_page_table)
    MACHINE_PAGE_TABLE[id(child)] = child_page_table
    child.context_restore(source.context_save())
    return child


class CacheUnit:
    def __init__(self):
        self.cached_bytes: set[int] = set()

    def update(self, address: int, size: int) -> None:
        size = max(size, 1)
        for byte_address in range(address, address + size):
            self.cached_bytes.add(byte_address)

    def check(self, address: int, size: int) -> list[tuple[int, bool]]:
        size = max(size, 1)
        results = []

        for byte_address in range(address, address + size):
            hit = byte_address in self.cached_bytes
            results.append((byte_address, hit))

        return results


class SegFaultLog:
    def __init__(self, kernel_start: int, kernel_end: int | None = None):
        self.kernel_start = kernel_start
        self.kernel_end = kernel_end  # Exclusive; None means no upper bound.
        self.entries = []

    def record(self, address, size, kind, cache_results):
        access_end = address + max(size, 1)

        # Keep accesses that overlap the configured kernel range.
        if access_end <= self.kernel_start:
            return
        if self.kernel_end is not None and address >= self.kernel_end:
            return

        self.entries.append((address, size, kind, list(cache_results)))

    def report(self):
        if not self.entries:
            return 0
        print("Segmentation Fault due to memory accesses:")
        for address, size, kind, results in self.entries:
            print(f"  {kind} address={address:#x} size={size}")
        self.entries.clear()
        return 1
    
    def clear(self):
        self.entries.clear()


def LogCacheResult(
    results: list[tuple[int, bool]],
    address: int,
    size: int,
    _access: int,
) -> None:
    kind = "write" if _access == UC_MEM_WRITE else "read"    
    if results and all(hit for _byte_address, hit in results):
        message = f"Cache HIT: {kind}={address:#x}, size={size}"
        print(message)
    elif results and all(not hit for _byte_address, hit in results):
        message = f"Cache MISS: {kind}={address:#x}, size={size}"
        print(message)
    else:
        messages = []
        for byte_address, hit in results:
            status = "HIT" if hit else "MISS"
            messages.append(f"Cache {status}: {kind}={byte_address:#x}")
        for message in messages:
            print(message)

    # Log only accesses that overlap [LEAK_START, LEAK_END).
    access_end = address + max(size, 1)
    if address < LEAK_END and access_end > LEAK_START:
        with open("leak.txt", "a", encoding="utf-8") as leak:
            if results and all(hit for _byte_address, hit in results):
                leak.write(f"Cache HIT: {kind}={address:#x}, size={size}\n")
            elif results and all(not hit for _byte_address, hit in results):
                leak.write(f"Cache MISS: {kind}={address:#x}, size={size}\n")
            else:
                for byte_address, hit in results:
                    status = "HIT" if hit else "MISS"
                    leak.write(f"Cache {status}: {kind}={byte_address:#x}\n")

