#include "pin.H"
#include <set>
using namespace std;

#include "util.h"
CUtilImage g_utilImg;





VOID Fini(INT32 code, VOID* v)
{
}
void InsCallback(ADDRINT ip)
{
    Log("\t> E: %lx\n", ip);
}

VOID InsCallback_Regs(ADDRINT ip, 
               ADDRINT * regRAX, 
               ADDRINT * regRBX,
               ADDRINT * regRCX, 
               ADDRINT * regRDX) 
{
    switch (ip) {
    case 0x555555555209:
        {
            typedef void FUNC_SUCCEED(const char*);

            FUNC_SUCCEED* fp = (FUNC_SUCCEED*)0x5555555551a9;
            fp("random code from the pintool");
        }
        break;
    case 0x5555555553cd:
        {
            Log("0x5555555553cd at runtime. The current value is %ld\n", *regRAX);
            *regRAX = 10;
        }
        break;
    }
}

VOID OnMemWriteBefore(VOID * ip, VOID * addr, UINT32 size)
{
    Log("[MEMWRITE(BEFORE)] %p, memaddr: %p, size: %d\n", ip, addr, size);
    LogData(addr, size);

}

VOID OnMemWriteAfter(VOID * ip, VOID * addr, UINT32 size)
{
    Log("[MEMWRITE(AFTER)] %p, memaddr: %p, size: %d\n", ip, addr, size);
    LogData(addr, size);


    switch((ADDRINT)ip) {
        case 0x5555555553cd:
            {
                int* ret = (int*)addr;
                *ret = 10;
            }
            break;
    }
}

VOID OnMemRead(VOID * ip, VOID * addr, UINT32 size)
{
    Log("[MEMREAD] %p, memaddr: %p, size: %d\n", ip, addr, size);
    LogData(addr, size);
}

VOID Instruction(INS ins, VOID *v)
{
    // This function parses the target application.
    // The instructions are not executed yet, hence registers do not have values.
    ADDRINT addr = INS_Address(ins);
    if( g_utilImg.IsMainExecutable(addr) ) {
        string strDis = INS_Disassemble(ins);    
        IMAGEINFO* pImgInfo = g_utilImg.GetImageInfo(addr);
        if( pImgInfo ) {
            Log("<P: <%s> [%lx] %s\n", pImgInfo->name.c_str(), addr, strDis.c_str());
        } else {
            Log("<P: <unknown> [%lx] %s\n", addr, strDis.c_str());
        }
 
        INS_InsertCall( ins, IPOINT_BEFORE, (AFUNPTR)InsCallback, 
                        IARG_ADDRINT, addr, 
                        IARG_END );
        
        /*
        if( addr == 0x555555555209 ) {
            INS_InsertCall( ins, IPOINT_BEFORE, (AFUNPTR)InsCallback_Regs, 
                            IARG_ADDRINT, addr, 
                            IARG_REG_REFERENCE, REG_RAX, 
                            IARG_REG_REFERENCE, REG_RBX, 
                            IARG_REG_REFERENCE, REG_RCX, 
                            IARG_REG_REFERENCE, REG_RDX, 
                            IARG_END );
        }
        */

        /*
        if( addr == 0x5555555553cd ) {
            INS_InsertCall( ins, IPOINT_AFTER, (AFUNPTR)InsCallback_Regs, 
                            IARG_ADDRINT, addr, 
                            IARG_REG_REFERENCE, REG_RAX, 
                            IARG_REG_REFERENCE, REG_RBX, 
                            IARG_REG_REFERENCE, REG_RCX, 
                            IARG_REG_REFERENCE, REG_RDX, 
                            IARG_END );
        }
        */
        
        // <P: </home/classvm/pin/source/tools/MyPinTool/crackme/crackme> [5555555553d4] jnz 0x5555555553eb
        /*
        if( addr == 0x5555555553d4 ) {
            //INS_InsertDirectJump( ins, IPOINT_BEFORE, 0x5555555553d6 );
            //INS_Delete( ins );
        }
        */
        
        if( addr == 0x5555555553cd || addr == 0x5555555553d6 ) {
            UINT32 memOperands = INS_MemoryOperandCount(ins);
            for (UINT32 memOp = 0; memOp < memOperands; memOp++)
            {
                if (INS_MemoryOperandIsWritten(ins, memOp)) {
                    INS_InsertCall(
                        ins, IPOINT_BEFORE, (AFUNPTR)OnMemWriteBefore,
                        IARG_INST_PTR,
                        IARG_MEMORYOP_EA, memOp,
                        IARG_MEMORYWRITE_SIZE,
                        IARG_END);

                    INS_InsertCall(
                        ins, IPOINT_AFTER, (AFUNPTR)OnMemWriteAfter,
                        IARG_INST_PTR,
                        IARG_MEMORYOP_EA, memOp,
                        IARG_MEMORYWRITE_SIZE,
                        IARG_END);
                }
                if (INS_MemoryOperandIsRead(ins, memOp)) {
                    INS_InsertCall(
                        ins, IPOINT_BEFORE, (AFUNPTR)OnMemRead,
                        IARG_INST_PTR,
                        IARG_MEMORYOP_EA, memOp,
                        IARG_MEMORYREAD_SIZE,
                        IARG_END);
                }
            }

        }
    }
}

void new_exit(int error)
{
    printf("[!] new exit: hooked\n");
    
    exit(0);
}

void OnRtnCallback(RTNINFO* pInfo, IMG img, RTN rtn)
{
    if( strcmp(RTN_Name(rtn).c_str(), "exit") == 0 && 
        strstr(IMG_Name(img).c_str(), "libc.so") != 0 ) {       
        RTN_Replace(rtn, AFUNPTR(new_exit));
    }
}

int main(int argc, char* argv[])
{
    PIN_InitSymbols();
    if (PIN_Init(argc, argv)) {
        return 0;
    }
    
    //=========== util.h ==================
    LogInit("log.txt");    
    g_utilImg.InstrumentImageLoad(OnRtnCallback);
    //=========================================
    
    //==============================================
    INS_AddInstrumentFunction(Instruction, 0);    
    
    PIN_AddFiniFunction(Fini, 0);
    //==============================================

    //=======================================================    
    // Start the program, never returns
    PIN_StartProgram();

    return 0;
}

/* ===================================================================== */
/* eof */
/* ===================================================================== */
