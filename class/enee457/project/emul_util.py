from capstone import *
from unicorn import *
from unicorn.x86_const import *
import os

#===============================================
#
# Global Variables
#
#===============================================


file_output = 0
old_eax = old_ebx = old_ecx = old_edx = old_edi = old_esi = old_esp = old_ebp = 0
valid_address_begin = valid_address_end = 0


#===============================================

def print_instruction(uc, address, size):
    mem = uc.mem_read(address, size)
    
    output = ("%x:" %(address))
    spc = 21
    for i in mem:
        tmp = (" %02x" %i)
        output = output + tmp
        spc = spc - 3
    out("%s%s%s" % (output, space(spc), dis(mem,address)))

#=============================================
# out(): printing outputs on the terminal and 
#        a file
#=============================================
def set_output_file(f):
    global file_output
    file_output = f

def close_output_file():
    global file_output
    file_output.close()
    
def out(str):
    global file_output
    print(str)
    print(str, file=file_output)

def read_string(uc, address):
    ret = ""
    c = uc.mem_read(address, 1)[0]
    read_bytes = 1

    while c != 0x0:
        ret += chr(c)
        c = uc.mem_read(address + read_bytes, 1)[0]
        read_bytes += 1
    return ret

def setpc(uc, pc):
    uc.reg_write(UC_X86_REG_EIP, pc)
    
def getpc(uc):
    pc = uc.reg_read(UC_X86_REG_EIP)
    return pc

def print_hexcode(code):
    cnt = 0
    last_return = 0
    for i in code:
        out(" %02x" %i, end="")
        cnt += 1
        last_return = 0
        if (cnt % 16) == 0:
            out("")
            last_return = 1
    if last_return == 0: out("")
    
def dis(mem, addr):
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    return '\n'.join([
        '%s %s' % (i.mnemonic, i.op_str)
        for i in md.disasm(mem, addr)
    ])

def space(num):
    return ''.join([
        ' ' for i in range(num)
    ])

def print_set(inst):
    for i in inst:
        out("%x" %i)
    out("total: %d" % len(inst))

def get_all_instructions(addr, code):
    inst = set()
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    
    # https://www.capstone-engine.org/lang_python.html
    for i in md.disasm(code, addr):
        inst.add(i.address)
    return inst


def save_set( varset, filename ):
    with open(filename, 'w') as f:
        for v in varset:
            f.write(str(v))
            f.write('\n')

def load_set( filename, ret_set ):
    with open(filename, 'r') as f:
        lines = f.readlines()
        for ln in lines:
            ret_set.add(int(ln))
    
def remove_set( setvar, elem ):
    try: 
        setvar.remove(elem)
    except:
        pass
    
def deletefile(filename):
    try:
        os.remove(filename)        
    except:
        pass



    
def get_validaddr_begin():
    global valid_address_begin
    return valid_address_begin
def get_validaddr_end():
    global valid_address_end
    return valid_address_end
  
def set_validaddr_range(addr_begin, addr_end):
    global valid_address_begin
    global valid_address_end
    valid_address_begin = addr_begin
    valid_address_end = addr_end

def is_validaddr(addr):
    if (addr < get_validaddr_begin()) or (addr > get_validaddr_end()):
        return False
    return True

def set_def_reg_values(uc):
    global old_eax, old_ebx, old_ecx, old_edx, old_edi, old_esi, old_esp, old_ebp
    old_eax = uc.reg_read(UC_X86_REG_EAX)
    old_ebx = uc.reg_read(UC_X86_REG_EBX)
    old_ecx = uc.reg_read(UC_X86_REG_ECX)
    old_edx = uc.reg_read(UC_X86_REG_EDX)
    old_edi = uc.reg_read(UC_X86_REG_EDI)
    old_esi = uc.reg_read(UC_X86_REG_ESI)
    old_esp = uc.reg_read(UC_X86_REG_ESP)
    old_ebp = uc.reg_read(UC_X86_REG_EBP)
        
def trace_reg_changes(uc):
	global old_eax, old_ebx, old_ecx, old_edx, old_edi, old_esi, old_esp, old_ebp
	eax = uc.reg_read(UC_X86_REG_EAX)
	ebx = uc.reg_read(UC_X86_REG_EBX)
	ecx = uc.reg_read(UC_X86_REG_ECX)
	edx = uc.reg_read(UC_X86_REG_EDX)
	edi = uc.reg_read(UC_X86_REG_EDI)
	esi = uc.reg_read(UC_X86_REG_ESI)
	esp = uc.reg_read(UC_X86_REG_ESP)
	ebp = uc.reg_read(UC_X86_REG_EBP)
	
	if( eax != old_eax ): out("\t| EAX: %08x" % (eax))
	if( ebx != old_ebx ): out("\t| EBX: %08x" % (ebx))
	if( ecx != old_ecx ): out("\t| ECX: %08x" % (ecx))
	if( edx != old_edx ): out("\t| EDX: %08x" % (edx))
	if( edi != old_edi ): out("\t| EDI: %08x" % (edi))
	if( esi != old_esi ): out("\t| ESI: %08x" % (esi))
	if( esp != old_esp ): out("\t| ESP: %08x" % (esp))
	if( ebp != old_ebp ): out("\t| EBP: %08x" % (ebp))
	old_eax = eax
	old_ebx = ebx
	old_ecx = ecx
	old_edx = edx
	old_edi = edi
	old_esi = esi
	old_esp = esp
	old_ebp = ebp


#==============================================
#
# trace functions (nothing special, just for logging)
#
#==============================================

def hook_mem(uci, access, address, size, value, user_data):
    ac = "UNKNOWN"
    if access == UC_MEM_WRITE: ac = "WR"
    elif access == UC_MEM_READ: ac = "RD"
        
    out("\t| Memory (%s): addr %x, size: %x, value: %x" % (ac, address, size, value))
    



def hook_syscall(uc, user_data):
    eax = uc.reg_read(UC_X86_REG_EAX)
    out("[SYSCALL] EAX = 0x%x" %(eax))
    uc.emu_stop()
