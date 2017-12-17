from ctypes import *
from ctypes.wintypes import *
import struct
import win32gui, win32process
from gym_nidhogg.envs import enum_modules

# help: https://stackoverflow.com/questions/33855690/trouble-with-readprocessmemory-in-python-to-read-64bit-process-memory


def print_address(address):
    print('0x{:08x}'.format(address))


def get_window_pid(title):
    hwnd = win32gui.FindWindow(None, title)
    threadid,pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid


def read_memory(process_handle, address):
    buff = c_ulonglong()
    val = c_ulonglong()
    bytes_read = c_ulong(0)
    try:
        if ReadProcessMemory(process_handle, address, byref(buff), 4, byref(bytes_read)):
            #memmove(ctypes.byref(val), buff, ctypes.sizeof(val))
            return buff.value
    except:
        print('proc_mem.read_memory failed - probably: ctypes.ArgumentError: argument 2: <class \'OverflowError\'>: int too long to convert')
    return 0


def track_address(process_handle, base_address, offsets):
    address = base_address
    for offset in offsets:
        address = read_memory(process_handle, address + offset)
        if address == 0:
            return 0
    return address  # = value


OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

PROCESS_ALL_ACCESS = 0x1F0FFF


def get_values_at_address(pid, base_address, offset_arrays=[[0]]):
    values = []  # multiple values can be returned with opening the process only once
    process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    for offsets in offset_arrays:
        values.append(track_address(process_handle, base_address, offsets))
    CloseHandle(process_handle)
    return values


if __name__ == '__main__':
    pid = get_window_pid("Nidhogg")
    base_address = enum_modules.find_base_address(pid, b'Nidhogg.exe')
    base_address = ctypes.addressof(base_address.contents)
    print(get_values_at_address(pid, base_address,
        [[0x0002CF08, 0x110, 0x38, 0x108, 0x108, 0x8C], [0x00194620, 0x108, 0x7C8, 0x10, 0x74, 0x84]]))
