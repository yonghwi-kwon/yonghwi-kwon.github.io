#!/usr/bin/env python3

from __future__ import print_function
from unicorn import *
from unicorn.x86_const import *
# sudo pip3 install capstone
from emul_util import *

import sys

#===============================================
#
# Global Variables
#
#===============================================
# memory address where emulation starts
ADDRESS = 0x1000000
inst_remain = set()
inst_executed = set()
inst_executed_local = set()
known_string = set()
remain_inst_filename = "continue_remain.txt"
execed_inst_filename = "continue_executed.txt"    
known_string_filename = "continue_executed.txt"    

load = False
load_state = False
# impl map/dictionary (cnt_repeated[addr] = cnt)
cnt_repeated = {}

#==============================================  
def save_sets():
    save_set( inst_remain, remain_inst_filename )
    save_set( inst_executed, execed_inst_filename )
    save_set( known_string, known_string_filename )

def load_sets(set_inst_remain, set_inst_executed, set_known_string):
    load_set( remain_inst_filename, set_inst_remain )
    load_set( execed_inst_filename, set_inst_executed )
    load_set( known_string_filename, set_known_string )
    
def delete_saved_sets():    
    deletefile(remain_inst_filename)
    deletefile(execed_inst_filename)
    deletefile(known_string_filename)

def save_mem_reg_state(uc):
    filename = "memdump.mem1.bin"
    # mem1 = read memory of ADDRESS (for 3MB)
    with open(filename, 'wb') as f:
        #f.write(mem1)
        pass
    filename = "memdump.mem2.bin"
    # mem2 = read memory of 0 (for 3MB)
    with open(filename, 'wb') as f:
        #f.write(mem2)
        pass
    
    filename = "regdump.txt"
    with open(filename, 'w') as f:
        # save register values
        # f.write(str(uc.reg_read(UC_X86_REG_EAX))); f.write('\n');
        pass
    
def load_mem_reg_state(uc):
    filename = "memdump.mem1.bin"
    with open(filename, 'rb') as f:
        mem1 = f.read()
        # write memory back (uc.mem_write)
    
    filename = "memdump.mem2.bin"
    with open(filename, 'rb') as f:
        mem2 = f.read()
        # write memory back (uc.mem_write)
    
    
    filename = "regdump.txt"
    with open(filename, 'r') as f:
        lines = f.readlines()
        i = 0
        for ln in lines:
            #if i == 0:  # eax
            #    uc.reg_write(UC_X86_REG_EAX, int(ln))
            i = i + 1
##########################################################################################


# callback for tracing instructions
def hook_code(uc, address, size, user_data):
    # read this instruction code from memory
    global inst_executed_local, inst_executed, inst_remain, known_string
    global cnt_repeated
    
    trace_reg_changes(uc)
    
    print_instruction(uc, address, size)    
    
    if is_validaddr(address) == False:
        out("Out of range: addr %x, addr range %x -- %x" % (address, get_validaddr_begin(), get_validaddr_end()))
        uc.emu_stop()
        return 
    elif address in inst_executed_local:
        if address in cnt_repeated:
            cnt_repeated[address] = cnt_repeated[address] + 1
        else:
            cnt_repeated[address] = 1
        output = "Already covered (stop analysis):: addr %x (repeated: %d)" % (address, cnt_repeated[address])
        out(output)
        uc.emu_stop()
        return 
    
    inst_executed.add(address)
    inst_executed_local.add(address)
    remove_set(inst_remain, address)


# callback for tracing invalid memory access (READ or WRITE)
def hook_mem_invalid(uc, access, address, size, value, user_data):
    # https://github.com/unicorn-engine/unicorn/blob/master/tests/regress/invalid_write.py
    ac = "UNKNOWN"
    if access == UC_MEM_WRITE: ac = "WR"
    elif access == UC_MEM_READ: ac = "RD"
    elif access == UC_MEM_READ_UNMAPPED: ac ="RD-UNMAPPED"
    elif access == UC_MEM_WRITE_UNMAPPED: ac ="WR-UNMAPPED"
    elif access == UC_MEM_FETCH_UNMAPPED: ac ="EX-UNMAPPED"
    
    if access == UC_MEM_FETCH_UNMAPPED:
        pc = 0
    else:
        pc = getpc(uc)
    
    output = ("\t<!> Invalid Memory Access (%s) (stop analysis): (PC: %x), MemAddr %x, Size: %x, Value: %x" % (ac, pc, address, size,value))
    out(output)
    uc.emu_stop()
    Finish(uc)
    quit()
    return False

    
def machine_reg_set(uc):    
    # initialize stack
    uc.reg_write(UC_X86_REG_ESP, ADDRESS + 0x200000)
    set_def_reg_values(uc)
    

def machine_memory_set(uc, code):
    # map 3MB memory for this emulation
    uc.mem_map(ADDRESS, 3 * 1024 * 1024)
    
    # map 3MB memory at 0
    uc.mem_map(0, 3 * 1024 * 1024)
    
    # write machine code to be emulated to memory
    uc.mem_write(ADDRESS, code)

    # =============================
    # map 1MB memory at 0
    #             5000000
    #uc.mem_map(0x5000000, 1024 * 1024)
    #             908c0000
    #uc.mem_map(0x908c0000, 1024 * 1024)
    # =============================

        
def Finish(uc):
    #out(">>> Emulation done")
    save_sets()
    save_mem_reg_state(uc)
    close_output_file()
    
def hook_interrupt(uc, intno, user_data):
    if intno == 0x3:
        out("[INTERRUPT] INT3 (breakpoint)")
        uc.emu_stop()
        return 
    elif intno != 0x80:
        out("[INTERRUPT] Unsupported %x" %intno);
        uc.emu_stop()
        return    

    eax = uc.reg_read(UC_X86_REG_EAX)
    eip = uc.reg_read(UC_X86_REG_EIP)
    ecx = uc.reg_read(UC_X86_REG_ECX)
    edx = uc.reg_read(UC_X86_REG_EDX)
    ebx = uc.reg_read(UC_X86_REG_EBX)
    esi = uc.reg_read(UC_X86_REG_ESI)
    
    if eax == 1:    # sys_exit
        out("[SYSCALL(INT 0x80)] SYS_EXIT at 0x%x" %(eip))
        uc.emu_stop()
    elif eax == 4:    # sys_write
        try:
            buf = uc.mem_read(ecx, edx)
            output = ("[SYSCALL(INT 0x80)] SYS_WRITE at 0x%x: Buffer = 0x%x, Size = %u, Content = " \
                        %(eip, ecx, edx))
            for i in buf:
                tmp = ("%02x" %i)
                output += tmp
            out(output)
        except UcError as e:
            output = ("[SYSCALL(INT 0x80)] SYS_WRITE at 0x%x: Buffer = 0x%x, Size = %u, Content = <unknown>" \
                        %(eip, ecx, edx))
            out(output)
    elif eax == 11:    # sys_execv
        global known_string        
        filename = read_string(uc, ebx)
        args = read_string(uc, esi)        
        output = ("[SYSCALL(INT 0x80)] SYS_EXECV (Path: '%s', Arg: '%s')" % (filename, args))
        out(output)
        
        # should terminate the analysis.
        uc.emu_stop()
        Finish(uc)
        return 
        #=========================================
    elif eax == 48:    # sys_signal ; http://asm.sourceforge.net/syscall.html
        # https://en.wikipedia.org/wiki/Signal_(IPC)
        # SIGTRAP	5	Terminate (core dump)	Trace/breakpoint trap
        output = ("[SYSCALL(INT 0x80)] SYS_SIGNAL (Signal: %x, Handler: %x)" % (ebx, ecx))
        out(output)
    ##############################
    else:
        out(">>> 0x%x: UNHANDLED interrupt 0x%x, EAX = 0x%x" %(eip, intno, eax))
        uc.emu_stop()
        return    

    
# Run X86 32 bit
def run_i386(mode, code):
    global inst_remain, inst_executed, known_string
    

    start_pc = ADDRESS
    if load == True:
        load_sets(inst_remain, inst_executed, known_string)
        
        if len(inst_remain) == 0:
            out("no remaining -- done")
            quit()
        else:
            inst_remain = sorted(inst_remain)
            start_pc = next(iter(inst_remain))
    else:
        inst_remain = get_all_instructions(ADDRESS, code)
    
        
    set_validaddr_range( ADDRESS, ADDRESS + len(code) )
    
    try:
        # Initialize emulator
        uc = Uc(UC_ARCH_X86, mode)
        
        # machine setting
        machine_memory_set(uc, code)
        machine_reg_set(uc)
        
        
        #
        # hooks
        #
        # tracing all instructions with customized callback
        uc.hook_add(UC_HOOK_CODE, hook_code)
        # tracing memory read/write
        uc.hook_add( UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, hook_mem )
        # tracing invalid memory read/write
        uc.hook_add( UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_INVALID, hook_mem_invalid )
        
        # tracing interrupts and syscalls
        uc.hook_add(UC_HOOK_INTR, hook_interrupt)
        uc.hook_add(UC_HOOK_INSN, hook_syscall, None, 1, 0, UC_X86_INS_SYSCALL)
        
        # emulate machine code in infinite time
        uc.emu_start( start_pc, ADDRESS + len(code) )

        # now print out some registers
        Finish(uc)
        
    except UcError as e:
        out("ERROR: %s" % e)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        if sys.argv[1] == "continue":
            load = True
            
    if len(sys.argv) >= 3:
        if sys.argv[2] == "loadstate":
            load_state = True
    
    if load == False:
        set_output_file(open("output.txt", "wt"))
        delete_saved_sets()
    else:
        set_output_file(open("output.txt", "at"))
    
    out("===========================================")

    #=========================================
    # Example 1:
    #=========================================
    # evasive (sample 1)
    CODE_EXAMPLE1 = b"\x6a\x30\x58\x6a\x05\x5b\xeb\x05\x59\xcd\x80\xcc\x40\xe8\xf6\xff\xff\xff\x99\xb0\x0b\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x52\x53\x54\xeb\xe1"
    
    #=========================================
    # Example 2:
    #=========================================
    # simple shellcode
    # should run with no problem.
    CODE_EXAMPLE2 = b"\x31\xc0\x50\x68//sh\x68/bin\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"
    
    
    #=========================================
    # Example 3:
    #=========================================
    # http://shell-storm.org/shellcode/files/shellcode-99.php
    CODE_EXAMPLE3 = b"\x31\xc0\x50\x50\xb0\x17\xcd\x80\xeb\x1f\x5e\x50\x68\x2f\x63\x61\x74\x68\x2f\x62\x69\x6e\x89\xe3\x50\x56\x53\x89\xe2\x50\x52\x53\xb0\x0b\x50\xcd\x80\x50\x50\xcd\x80\xe8\xdc\xff\xff\xff\x2f\x65\x74\x63\x2f\x6d\x61\x73\x74\x65\x72\x2e\x70\x61\x73\x73\x77\x64";
    
    #=========================================
    # Example 4:
    #=========================================
    # http://shell-storm.org/shellcode/files/shellcode-172.php
    # system call 23 is missing: 
    # see http://faculty.nps.edu/cseagle/assembly/sys_call.html for what is 23 (setuid)
    # TODO: 1. support setuid
    # 2. The last few bytes of the code is a string. 
    # the string is used in the 'execve' syscall. Detect the string's addr, and 
    # prevent the program from executing a string.
    # 3. execve should not return.
    CODE_EXAMPLE4 =     b"\xeb\x2c\x5e\x31\xc0\xb0\x17\x50\xcd\x80\x31\xc0\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x50\x66\x68\x2d\x63\x89\xe7\x50\x56\x57\x53\x89\xe7\x50\x57\x53\x50\xb0\x0b\xcd\x80\xe8\xcf\xff\xff\xff\x2f\x73\x62\x69\x6e\x2f\x6b\x6c\x64\x6c\x6f\x61\x64\x20\x2f\x74\x6d\x70\x2f\x6f\x2e\x6f";
    
    #=========================================
    # Example 5:
    #=========================================
    # encrypted shellcode
    # http://shell-storm.org/shellcode/files/shellcode-168.php
    ## 31 d2 eb 0e 31 db 5b b1 19 83 2c 1a 01 42 e2 f9 eb 05 e8 ed ff ff ff 32 c1 51 69 30 30 74 69 69 30 63 6a 6f 32 dc 8a e4 51 55 54 51 b1 3c ce 81
    ## ==>
    ## ## 31 d2 eb 0e 31 db 5b b1 19 83 2c 1a 01 42 e2 f9 eb 05 e8 ed ff ff ff 32 c1 51 69 30 30 74 69 69 30 63 6a 6f 32 dc 8a e4 51 55 54 51 b1 0c ce 81    
    CODE_EXAMPLE5 = b"\x31\xd2\xeb\x0e\x31\xdb\x5b\xb1\x19\x83\x2c\x1a\x01\x42\xe2\xf9\xeb\x05\xe8\xed\xff\xff\xff\x32\xc1\x51\x69\x30\x30\x74\x69\x69\x30\x63\x6a\x6f\x32\xdc\x8a\xe4\x51\x55\x54\x51\xb1\x0c\xce\x81";


    run_i386(UC_MODE_32, CODE_EXAMPLE1)

