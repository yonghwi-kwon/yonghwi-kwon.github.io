#include <map>
#include <vector>
using namespace std;

typedef struct tag_RTNINFO {
    string name;
    ADDRINT addr;
    USIZE size;
} RTNINFO;

typedef struct tag_IMAGEINFO {
    string name;
    ADDRINT addrLow;
    ADDRINT addrHigh;
    USIZE size;
    BOOL bMainExec;
    vector<RTNINFO*> vtRoutine;    
} IMAGEINFO;

typedef void (*FP_RTN_CALLBACK)(RTNINFO* pInfo, IMG img, RTN rtn);

FILE* g_pLogFile = 0;



int LogInit(const char* filename)
{
    if( filename == 0 ) {
        filename = "log.txt";
    }
    g_pLogFile = fopen(filename, "wt");

    return (g_pLogFile != 0);
}
void Log(const char *format, ...)
{
    va_list ap;
    char buf[8192];

    va_start(ap, format);
    vsprintf(buf, format, ap);
    va_end(ap);

    if( g_pLogFile ) {
        fputs(buf, g_pLogFile);
    } else {    
        puts(buf);
    }
}
void LogData(VOID* addr, UINT32 size)
{
    unsigned char* p = (unsigned char*)addr;
    for( unsigned  int i = 0; i < size; i++ ) {
        Log("%02x ", (unsigned char)*p);
        p++;
    }
    Log("\n");
}







#define UNINIT_EXIT() if( m_bInited == FALSE ) {\
            printf("Call CImageLoadInfo::InstrumentImageLoad first. Not initialized.\n"); exit(0);\
            return FALSE;\
        }
typedef struct tag_IMAGELOAD_ARG {
    FP_RTN_CALLBACK fpCallback;
    map<ADDRINT, IMAGEINFO*> *pMap;
    RTNINFO* pMainRtn;
} IMAGELOAD_ARG;

class CUtilImage {
public:
    CUtilImage() {
        m_bInited = FALSE;
        m_pMainRtn = 0;
    };
    ~CUtilImage() {
        m_bInited = FALSE;
    }
    void InstrumentImageLoad(FP_RTN_CALLBACK fpRtnCallback)
    {
        m_stImageLoadArg.fpCallback = fpRtnCallback;
        m_stImageLoadArg.pMap = &m_mapImage;
        IMG_AddInstrumentFunction(CUtilImage::OnImageLoad, (VOID*)&m_stImageLoadArg);
        m_bInited = TRUE;
    }

    BOOL IsMainExecutable(ADDRINT addr) 
    {
        UNINIT_EXIT();
        IMAGEINFO* p = GetImageInfo(addr);
        if( p ) {
            return p->bMainExec;
        }
        return FALSE;
    }

    const char* GetImageName(ADDRINT addr)
    {
        IMAGEINFO* p = GetImageInfo(addr);
        if( p ) {
            return p->name.c_str();
        }
        return "unknown";
    }

    int IsMainRoutine(ADDRINT addr) 
    {
        RTNINFO* p = GetMainRoutineInfo();
        if( p ) {
            if( p->addr <= addr && addr < (p->addr + p->size) ) {
                return 1;
            }
        }
        return 0;
    }

    RTNINFO* GetMainRoutineInfo()
    {
        map<ADDRINT, IMAGEINFO*>::iterator it;

        if( m_pMainRtn ) {
            return m_pMainRtn;
        }

        for( it = m_mapImage.begin(); it != m_mapImage.end(); it++ ){
            IMAGEINFO* p = it->second;

            if( p->bMainExec ) {
                vector<RTNINFO*>::iterator itr; // vtRoutine;    
                for( itr = p->vtRoutine.begin(); itr != p->vtRoutine.end(); itr++ ){
                    RTNINFO* pRtn = *itr;

                    if( pRtn ) {
                        if( strcmp( pRtn->name.c_str(), "main" ) == 0 ) {
                            m_pMainRtn = pRtn;
                            break;
                        }
                    }
                }
                break;
            }
        }
        return m_pMainRtn;
    }


    IMAGEINFO* GetImageInfo(ADDRINT addr) 
    {
        map<ADDRINT, IMAGEINFO*>::iterator it;

        for( it = m_mapImage.begin(); it != m_mapImage.end(); it++ ){
            IMAGEINFO* p = it->second;

            if( p->addrLow <= addr && addr < p->addrHigh ) {
                return p;
            }
        }
        return 0;
    }

private:
    static VOID OnImageLoad(IMG img, VOID *v)
    {
        IMAGELOAD_ARG* pImageLoadArg = (IMAGELOAD_ARG*)v;

        IMAGEINFO* pImg = SaveImageInfo(img, pImageLoadArg->pMap);
        
        for( SEC sec = IMG_SecHead(img); SEC_Valid(sec); sec = SEC_Next(sec) ) {
            for( RTN rtn = SEC_RtnHead(sec); RTN_Valid(rtn); rtn = RTN_Next(rtn) ) {
                RTNINFO* p = new RTNINFO;

                p->name = RTN_Name( rtn );
                p->addr = RTN_Address( rtn );
                p->size = RTN_Size( rtn );

                //Log("Routine: %s, %lx, %ld\n", p->name.c_str(), p->addr, p->size);
                
                pImg->vtRoutine.push_back( p );
                
                if( pImageLoadArg->fpCallback ) {
                    pImageLoadArg->fpCallback(p, img, rtn);
                }
            }
        }
    }
    static IMAGEINFO* SaveImageInfo(IMG img, map<ADDRINT, IMAGEINFO*>* pmapImage)
    {
        ADDRINT addrLow = IMG_LowAddress(img);
        map<ADDRINT, IMAGEINFO*>::iterator it;

        it = pmapImage->find(addrLow); 
        
        IMAGEINFO* p = 0;
        if( it != pmapImage->end() ) { // found
            //printf("found\n");
            p = it->second;
        } else { // new
            p = new IMAGEINFO;
            p->addrHigh = IMG_HighAddress(img);
            p->addrLow = addrLow;
            p->size = IMG_SizeMapped(img);
            p->name = IMG_Name(img);
            p->bMainExec = IMG_IsMainExecutable(img);
            pmapImage->insert( make_pair(addrLow, p) );

            //Log("Image: %s, %lx ~ %lx, %ld, %d\n", p->name.c_str(), p->addrLow, p->addrHigh, p->size, p->bMainExec);
        }
        return p;
    }
private:
    BOOL m_bInited;
    map<ADDRINT, IMAGEINFO*> m_mapImage;
    IMAGELOAD_ARG m_stImageLoadArg;
    RTNINFO* m_pMainRtn;
};
