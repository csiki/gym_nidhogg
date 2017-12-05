from ctypes import *
from ctypes.wintypes import *
import sys
import win32gui, win32process


def get_window_pid(title):
    hwnd = win32gui.FindWindow(None, title)
    threadid,pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid


# from: https://stackoverflow.com/questions/9763459/how-to-enumerate-modules-in-python-64bit
# const variable
# Establish rights and basic options needed for all process declartion / iteration
TH32CS_SNAPPROCESS = 2
STANDARD_RIGHTS_REQUIRED = 0x000F0000
SYNCHRONIZE = 0x00100000
PROCESS_ALL_ACCESS = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFF)
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPTHREAD = 0x00000004

#class MODULEENTRY32(Structure):
#    _fields_ = [ ( 'dwSize' , DWORD ) , 
#                ( 'th32ModuleID' , DWORD ),
#                ( 'th32ProcessID' , DWORD ),
#                ( 'GlblcntUsage' , DWORD ),
#                ( 'ProccntUsage' , DWORD ) ,
#                ( 'modBaseAddr' , LONG ) ,
#                ( 'modBaseSize' , DWORD ) , 
#                ( 'hModule' , HMODULE ) ,
#                ( 'szModule' , c_char * 256 ),
#                ( 'szExePath' , c_char * 260 ) ]


class MODULEENTRY32(Structure):
    _fields_ = [( 'dwSize' , DWORD ) , 
                ( 'th32ModuleID' , DWORD ),
                ( 'th32ProcessID' , DWORD ),
                ( 'GlblcntUsage' , DWORD ),
                ( 'ProccntUsage' , DWORD ) ,
                ( 'modBaseAddr' , POINTER(BYTE) ) ,
                ( 'modBaseSize' , DWORD ) , 
                ( 'hModule' , HMODULE ) ,
                ( 'szModule' , c_char * 256 ),
                ( 'szExePath' , c_char * 260 ) ]


CreateToolhelp32Snapshot= windll.kernel32.CreateToolhelp32Snapshot
Process32First = windll.kernel32.Process32First
Process32Next = windll.kernel32.Process32Next
Module32First = windll.kernel32.Module32First
Module32Next = windll.kernel32.Module32Next
GetLastError = windll.kernel32.GetLastError
OpenProcess = windll.kernel32.OpenProcess
GetPriorityClass = windll.kernel32.GetPriorityClass
CloseHandle = windll.kernel32.CloseHandle

def find_base_address(pid, module_name):
    try:
        ProcessID=pid
        hModuleSnap = DWORD
        me32 = MODULEENTRY32()
        me32.dwSize = sizeof( MODULEENTRY32 )
        #me32.dwSize = 5000
        hModuleSnap = CreateToolhelp32Snapshot( TH32CS_SNAPMODULE, ProcessID )
        ret = Module32First( hModuleSnap, pointer(me32) )
        if ret == 0:
            print('ListProcessModules() Error on Module32First[{}]').format(GetLastError())
            CloseHandle( hModuleSnap )
        global PROGMainBase
        PROGMainBase=False

        base_address = None
        while ret:
            if me32.szModule == module_name:
                base_address = me32.modBaseAddr
                break
            # print(me32.dwSize)
            # print(me32.th32ModuleID)
            # print(me32.th32ProcessID)
            # print(me32.GlblcntUsage)
            # print(me32.ProccntUsage)
            # print(me32.modBaseAddr)
            # print(me32.modBaseSize)
            # print(me32.hModule)
            # print(me32.szModule)
            # print(me32.szExePath)
            ret = Module32Next( hModuleSnap , pointer(me32) )
    except:
        print("Error in ListProcessModules")
    finally:
        CloseHandle( hModuleSnap )

    return base_address


if __name__ == '__main__':
    base_address = find_base_address(get_window_pid("Nidhogg"), b'Nidhogg.exe')
    print(dir(base_address))
    print(hex(ctypes.addressof(base_address.contents)))
