"""Software page-table configuration and Unicorn mapping application."""

from __future__ import annotations

from dataclasses import dataclass, field

from unicorn import (
    Uc,
    UC_PROT_ALL,
    UC_PROT_EXEC,
    UC_PROT_READ,
    UC_PROT_WRITE,
)

PAGE_SIZE = 0x1000


@dataclass
class PageTableEntry:
    """Configuration for one emulated virtual page."""

    present: bool = True
    permissions: int = UC_PROT_ALL
    contents: bytearray = field(default_factory=lambda: bytearray(PAGE_SIZE))


class PageTable:
    """A software table; editing entries alone does not change Unicorn memory."""

    def __init__(self):
        self.entries: dict[int, PageTableEntry] = {}
        # Tracks what map_page_table() most recently applied to a Uc instance.
        self.applied: dict[int, int | None] = {}

    @staticmethod
    def page_base(address: int) -> int:
        return address & ~(PAGE_SIZE - 1)

    def add_page(
        self,
        address: int,
        permissions: int = UC_PROT_ALL,
        contents: bytes | bytearray | None = None,
        present: bool = True,
    ) -> PageTableEntry:
        """Add a page configuration without mapping it in Unicorn yet."""
        base = self.page_base(address)
        entry = self.entries.get(base)
        if entry is None:
            entry = PageTableEntry(present=present, permissions=permissions)
            self.entries[base] = entry
            self.applied[base] = None
        else:
            entry.present = entry.present or present
            entry.permissions |= permissions

        if contents is not None:
            if len(contents) > PAGE_SIZE:
                raise ValueError("page contents cannot exceed one page")
            entry.contents[: len(contents)] = contents
        return entry

    def lookup(self, address: int) -> PageTableEntry | None:
        return self.entries.get(self.page_base(address))

    def set_present(self, address: int, present: bool) -> None:
        """Change the software PTE only. Call map_page_table() to apply it."""
        base = self.page_base(address)
        if base not in self.entries:
            raise ValueError(f"no page-table entry for {base:#x}")
        self.entries[base].present = present

    def set_range_present(self, address: int, size: int, present: bool) -> None:
        """Change present bits for a page-aligned range; no Unicorn calls yet."""
        self._check_range(address, size)
        bases = list(range(address, address + size, PAGE_SIZE))
        missing = [base for base in bases if base not in self.entries]
        if missing:
            raise ValueError(f"no page-table entry for {missing[0]:#x}")
        for base in bases:
            self.entries[base].present = present

    def clone_current(self, source: Uc) -> "PageTable":
        """Copy the table, taking current RAM bytes from the source emulator."""
        child = PageTable()
        for base, entry in self.entries.items():
            contents = (
                bytearray(source.mem_read(base, PAGE_SIZE))
                if entry.present
                else bytearray(entry.contents)
            )
            child.entries[base] = PageTableEntry(
                present=entry.present,
                permissions=entry.permissions,
                contents=contents,
            )
            child.applied[base] = None
        return child

    @staticmethod
    def _check_range(address: int, size: int) -> None:
        if address % PAGE_SIZE or size <= 0 or size % PAGE_SIZE:
            raise ValueError(
                f"address and positive size must be multiples of {PAGE_SIZE:#x}"
            )


def map_page_table(uc: Uc, page_table: PageTable) -> None:
    """Apply PTE changes using Unicorn's mem_map, mem_unmap, and mem_protect."""
    for base in sorted(page_table.entries):
        entry = page_table.entries[base]
        old_permissions = page_table.applied.get(base)

        if entry.present and old_permissions is None:
            uc.mem_map(base, PAGE_SIZE, entry.permissions)
            uc.mem_write(base, bytes(entry.contents))
            page_table.applied[base] = entry.permissions
        elif not entry.present and old_permissions is not None:
            # Save current bytes before removing RAM so a later remap restores them.
            entry.contents[:] = uc.mem_read(base, PAGE_SIZE)
            uc.mem_unmap(base, PAGE_SIZE)
            page_table.applied[base] = None
        elif entry.present and old_permissions != entry.permissions:
            uc.mem_protect(base, PAGE_SIZE, entry.permissions)
            page_table.applied[base] = entry.permissions


def elf_flags_to_unicorn(flags: int) -> int:
    """Translate ELF PF_R/PF_W/PF_X bits to Unicorn permissions."""
    permissions = 0
    if flags & 4:  # ELF PF_R
        permissions |= UC_PROT_READ
    if flags & 2:  # ELF PF_W
        permissions |= UC_PROT_WRITE
    if flags & 1:  # ELF PF_X
        permissions |= UC_PROT_EXEC
    return permissions or UC_PROT_ALL


MACHINE_PAGE_TABLE: dict[int, PageTable] = {}


