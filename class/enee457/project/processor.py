#!/usr/bin/env python3

from __future__ import annotations
import argparse
from pathlib import Path
from capstone import CS_ARCH_X86, CS_GRP_JUMP, CS_MODE_64, Cs
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
from unicorn.x86_const import UC_X86_REG_RDI, UC_X86_REG_RIP, UC_X86_REG_RSP
from processor_lib import (
    PAGE,
    KERNEL_BUF_ADDR,
    ElfImage,
    LabError,
    compile_victim,
    load_cached_symbols,
    map_image,
    read_elf64,
    find_branch_starts_and_merge, 
    clone_uc_state,
    CacheUnit,
    SegFaultLog,
    LogCacheResult,
)
from page_table import (
    MACHINE_PAGE_TABLE,
    PAGE_SIZE,
    PageTable,
    elf_flags_to_unicorn,
    map_page_table,
)

STACK_BASE = 0x70000000
STACK_SIZE = 0x20000
STOP_ADDR = 0x71000000
STOP_PAGE = STOP_ADDR & ~(PAGE - 1)
PROBE_ENTRIES = 256
KERNEL_SPACE = 0xC0000000
INPUT = 0xBADF00D

segfault_taken = SegFaultLog(KERNEL_SPACE)
segfault_fallthrough = SegFaultLog(KERNEL_SPACE)



# ========================================================================
# DO NOT CHANGE THE CODE ABOVE
# ========================================================================

# ========================================================================
# YOUR SOLUTION BEGINS

def OnSpeculativeMemoryAccess(_uc: Uc, _access: int, address: int, size: int, _value: int, _data: object, cache: CacheUnit, segfault_log: SegFaultLog) -> None:
    # print(f"speculative memory access: address={address:#x} size={size}")
    segfault_log.record(address, size, ("write" if _access == UC_MEM_WRITE else "read"), cache.check(address, size))
    cache.update(address, size)

def OnMemoryAccess(_uc: Uc, _access: int, address: int, size: int, _value: int, _data: object, cache: CacheUnit) -> None:
    results = cache.check(address, size)
    cache.update(address, size)
    LogCacheResult(results, address, size, _access)


def OnSpeculativeBegin(taken_child: Uc, fallthrough_child: Uc, taken_page_table: PageTable, fallthrough_page_table: PageTable):
    return 

def OnSpeculativeEnd(taken_child: Uc, fallthrough_child: Uc):
    return 

# YOUR SOLUTION ENDS
# ========================================================================

# ========================================================================
# DO NOT CHANGE THE CODE BELOW
# ========================================================================



def new_machine(
    image: ElfImage,
    cache: CacheUnit,
    input_value: int,
    victim_addr: int,
    victim_size: int,
    handoff: dict[str, Uc] | None = None,
) -> Uc:
    if not any(
        start <= KERNEL_BUF_ADDR < start + memory_size
        for start, memory_size, _contents, _flags in image.loads
    ):
        raise LabError(f"ELF has no loadable segment covering kernel_buf at {KERNEL_BUF_ADDR:#x}")
    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    page_table = map_image(uc, image)
    for page in range(STACK_BASE, STACK_BASE + STACK_SIZE, PAGE):
        page_table.add_page(page, permissions=UC_PROT_ALL)

    page_table.add_page(STOP_PAGE, permissions=UC_PROT_ALL)
    map_page_table(uc, page_table)
    MACHINE_PAGE_TABLE[id(uc)] = page_table

    uc.mem_write(STACK_BASE + STACK_SIZE - 8, STOP_ADDR.to_bytes(8, "little"))
    uc.reg_write(UC_X86_REG_RSP, STACK_BASE + STACK_SIZE - 8)
    uc.reg_write(UC_X86_REG_RDI, input_value) 

    # =================================================================
    def on_memory(_uc: Uc, _access: int, address: int, size: int, _value: int, _data: object) -> None:
        OnMemoryAccess(_uc, _access, address, size, _value, _data, cache)
    # =================================================================
        
    disasm = Cs(CS_ARCH_X86, CS_MODE_64)
    disasm.detail = True
    def on_instruction(emu: Uc, address: int, size: int, _data: object) -> None:
        if address == STOP_ADDR:
            emu.emu_stop()
            return

        code = bytes(emu.mem_read(address, size))
        instruction = next(disasm.disasm(code, address), None)

        if instruction:
            print(f"{address:#018x}: {instruction.mnemonic:<8} {instruction.op_str}")
        else:
            print(f"{address:#018x}: <could not disassemble>")

        if (instruction
            and instruction.group(CS_GRP_JUMP)
            and instruction.mnemonic.lower() not in ("jmp", "ljmp")):
            taken_start, fallthrough_start, merge = find_branch_starts_and_merge(emu, address, victim_addr, victim_size)

            if taken_start == merge or fallthrough_start == merge:
                # print("No transient execution: one path merges immediately.")
                return

            print("="*50)
            print(f"taken:        {taken_start:#x}")
            print(f"fall-through: {fallthrough_start:#x}")
            print(f"merge:        {merge:#x}")

            branch_probe = clone_uc_state(emu)
            branch_probe.emu_start(address, 0, count=1)
            actual_next = branch_probe.reg_read(UC_X86_REG_RIP)
            
            # =================================================================
            def on_spec_memory_taken(_uc: Uc, _access: int, address: int, size: int, _value: int, _data: object) -> None:
                OnSpeculativeMemoryAccess(_uc, _access, address, size, _value, _data, cache, segfault_taken)                
            def on_spec_memory_fallthrough(_uc: Uc, _access: int, address: int, size: int, _value: int, _data: object) -> None:
                OnSpeculativeMemoryAccess(_uc, _access, address, size, _value, _data, cache, segfault_fallthrough)                
            def on_invalid_memory(uc: Uc, access: int, address: int, size: int, value: int, _data: object) -> bool:
                print(
                    f"Invalid memory access: address={address:#x}, "
                    f"size={size}, access={access:#x}, value={value:#x}"
                )
                return True
            # =================================================================


            taken_child = clone_uc_state(emu)
            taken_child.reg_write(UC_X86_REG_RIP, taken_start)
            hook_handle_taken = taken_child.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, on_spec_memory_taken)
            taken_child.hook_add(UC_HOOK_MEM_INVALID, on_invalid_memory)            
            
            fallthrough_child = clone_uc_state(emu)
            fallthrough_child.reg_write(UC_X86_REG_RIP, fallthrough_start)
            hook_handle_fallthrough = fallthrough_child.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, on_spec_memory_fallthrough)
            fallthrough_child.hook_add(UC_HOOK_MEM_INVALID, on_invalid_memory)

            taken_page_table = MACHINE_PAGE_TABLE[id(taken_child)]
            fallthrough_page_table = MACHINE_PAGE_TABLE[id(fallthrough_child)]

            OnSpeculativeBegin(taken_child, fallthrough_child, taken_page_table, fallthrough_page_table)
            
            try:
                taken_child.emu_start(taken_start, merge, count=100_000)
            except UcError as exc:
                print(f"Taken fault at RIP={taken_child.reg_read(UC_X86_REG_RIP):#x} {exc}")
                

            try:
                fallthrough_child.emu_start(fallthrough_start, merge, count=100_000)
            except UcError as exc:
                print(f"Fall-through fault at RIP={fallthrough_child.reg_read(UC_X86_REG_RIP):#x} {exc}")
                
            

            OnSpeculativeEnd(taken_child, fallthrough_child)
            
            taken_child.hook_del(hook_handle_taken)
            fallthrough_child.hook_del(hook_handle_fallthrough)
            


            path = "taken" if actual_next == taken_start else "fall-through"
            print(f"Current execution takes: {path}")
            print("="*50)
            
            if actual_next == taken_start: 
                chosen_child = taken_child
                if segfault_taken.report():
                    emu.emu_stop()
                    return 
                segfault_fallthrough.clear()
            else:
                chosen_child = fallthrough_child
                if segfault_fallthrough.report():
                    emu.emu_stop()
                    return 
                segfault_taken.clear()

            # Install hooks because clones do not inherit callbacks.
            chosen_child.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, on_memory)
            chosen_child.hook_add(UC_HOOK_CODE, on_instruction)

            if handoff is not None:
                handoff["machine"] = chosen_child
                emu.emu_stop()
            return
            
    uc.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, on_memory)
    uc.hook_add(UC_HOOK_CODE, on_instruction)
    return uc

def run_machine(image: ElfImage, cache: CacheUnit, input_value: int, victim_addr: int, victim_size: int) -> None:
    handoff = {}
    active = new_machine( image, cache, input_value, victim_addr, victim_size, handoff )
    pc = image.entry
    while True:
        active.emu_start(pc, STOP_ADDR, count=100_000)

        next_machine = handoff.pop("machine", None)
        if next_machine is None:
            break

        active = next_machine
        pc = active.reg_read(UC_X86_REG_RIP)

def main() -> None:
    Path("leak.txt").unlink(missing_ok=True)    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="compile victim.c once and save reusable outputs")
    parser.add_argument("--source", type=Path, default=Path(__file__).with_name("victim.c"), help="C source used only with --build")
    parser.add_argument("--build-dir", type=Path, default=Path(__file__).with_name("build"), help="directory for reusable build outputs")
    parser.add_argument("--cc", default="gcc", help="C compiler (default: gcc)")
    parser.add_argument("--nm", default="nm", help="symbol-table utility (default: nm)")
    args = parser.parse_args()
    try:
        elf_path = args.build_dir / "victim.elf"
        assembly_path = args.build_dir / "victim.s"
        symbols_path = args.build_dir / "victim_symbols.json"
        if args.build:
            if not args.source.is_file():
                parser.error(f"source file not found: {args.source}")
            elf_path, symbols = compile_victim(args.source, args.cc, args.nm, args.build_dir)
            print(f"Built reusable ELF: {elf_path}")
            print(f"Saved compiler assembly: {assembly_path}")
            print(f"Saved symbol metadata: {symbols_path}")
            return
        if not elf_path.is_file() or not assembly_path.is_file() or not symbols_path.is_file():
            parser.error(f"build outputs are missing; run once with --build (build directory: {args.build_dir})")
        symbols = load_cached_symbols(symbols_path)
        if symbols["kernel_buf"][0] != KERNEL_BUF_ADDR:
            raise LabError(
                f"cached kernel_buf address is {symbols['kernel_buf'][0]:#x}, "
                f"not {KERNEL_BUF_ADDR:#x}; rebuild with --build"
            )
        image = read_elf64(elf_path)
        victim_addr, victim_size = symbols["victim"]

        cache = CacheUnit()
        print("="*50)
        print(f"Input: 0x{INPUT:X}")
        print(f"  - User buffer   : {symbols['user_buf'][0]:#x}")
        print(f"  - Kernel buffer : {symbols['kernel_buf'][0]:#x}")
        print("="*50)
        
        run_machine(image, cache, INPUT, victim_addr, victim_size)

    except (LabError, OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()


