""" Make screenshots of windows on Windows and Linux.
We need this to do visual tests.
"""

# from: https://programtalk.com/vs2/python/14544/flexx/flexx/util/screenshot.py/

import sys
import numpy as np
import matplotlib.pyplot as plt
 
import ctypes
import win32gui
from ctypes import windll
from ctypes.wintypes import (BOOL, DOUBLE, DWORD, HBITMAP, HDC, HGDIOBJ,  # noqa
                             HWND, INT, LPARAM, LONG, UINT, WORD)  # noqa
 
SRCCOPY = 13369376
DIB_RGB_COLORS = BI_RGB = 0
 
class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long)]
 
class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [('biSize', DWORD), ('biWidth', LONG), ('biHeight', LONG),
                    ('biPlanes', WORD), ('biBitCount', WORD),
                    ('biCompression', DWORD), ('biSizeImage', DWORD),
                    ('biXPelsPerMeter', LONG), ('biYPelsPerMeter', LONG),
                    ('biClrUsed', DWORD), ('biClrImportant', DWORD)]
 
class BITMAPINFO(ctypes.Structure):
    _fields_ = [('bmiHeader', BITMAPINFOHEADER), ('bmiColors', DWORD * 3)]
 
# Function shorthands
GetClientRect = windll.user32.GetClientRect
GetWindowRect = windll.user32.GetWindowRect
PrintWindow = windll.user32.PrintWindow
GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId
IsWindowVisible = windll.user32.IsWindowVisible
EnumWindows = windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool,
                                     ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int))
 
GetWindowDC = windll.user32.GetWindowDC
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
SelectObject = windll.gdi32.SelectObject
BitBlt = windll.gdi32.BitBlt
DeleteObject = windll.gdi32.DeleteObject
GetDIBits = windll.gdi32.GetDIBits
 
# Arg types
windll.user32.GetWindowDC.argtypes = [HWND]
windll.gdi32.CreateCompatibleDC.argtypes = [HDC]
windll.gdi32.CreateCompatibleBitmap.argtypes = [HDC, INT, INT]
windll.gdi32.SelectObject.argtypes = [HDC, HGDIOBJ]
windll.gdi32.BitBlt.argtypes = [HDC, INT, INT, INT, INT, HDC, INT, INT, DWORD]
windll.gdi32.DeleteObject.argtypes = [HGDIOBJ]
windll.gdi32.GetDIBits.argtypes = [HDC, HBITMAP, UINT, UINT, ctypes.c_void_p,
                                    ctypes.POINTER(BITMAPINFO), UINT]
# Return types
windll.user32.GetWindowDC.restypes = HDC
windll.gdi32.CreateCompatibleDC.restypes = HDC
windll.gdi32.CreateCompatibleBitmap.restypes = HBITMAP
windll.gdi32.SelectObject.restypes = HGDIOBJ
windll.gdi32.BitBlt.restypes = BOOL
windll.gdi32.GetDIBits.restypes = INT
windll.gdi32.DeleteObject.restypes = BOOL
 
 
def screenshot(window_name, client=True):
    """ Grab a screenshot of the first visible window of the process
    with the given id. If client is True, no Window decoration is shown.
     
    This code is derived from https://github.com/BoboTiG/python-mss
    """
    # Get handle
    hwnd = win32gui.FindWindow(None, window_name)
    # Get window dimensions
    rect = RECT()
    if client:
        GetClientRect(hwnd, ctypes.byref(rect))
    else:
        GetWindowRect(hwnd, ctypes.byref(rect))
    left, right, top, bottom = rect.left, rect.right, rect.top, rect.bottom
    w, h = right - left, bottom - top
     
    hwndDC = saveDC = bmp = None
    try:
        # Get device contexts
        hwndDC = GetWindowDC(hwnd)
        saveDC = CreateCompatibleDC(hwndDC)
        # Get bitmap
        bmp = CreateCompatibleBitmap(hwndDC, w, h)
        SelectObject(saveDC, bmp)
        if client:
            PrintWindow(hwnd, saveDC, 1)  # todo: result is never used??
        else:
            PrintWindow(hwnd, saveDC, 0)
        # Init bitmap info
        # We grab the image in RGBX mode, so that each word is 32bit and
        # we have no striding, then we transform to RGB
        buffer_len = h * w * 4
        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = w
        bmi.bmiHeader.biHeight = -h  # Why minus? See [1]
        bmi.bmiHeader.biPlanes = 1  # Always 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = BI_RGB
        # Blit
        image = ctypes.create_string_buffer(buffer_len)
        bits = windll.gdi32.GetDIBits(saveDC, bmp, 0, h, image, bmi, DIB_RGB_COLORS)
        assert bits == h
        # Replace pixels values: BGRX to RGB
        image2 = ctypes.create_string_buffer(h*w*3)
        image2[0::3] = image[2::4]
        image2[1::3] = image[1::4]
        image2[2::3] = image[0::4]
         
        return bytes(image2), (w, h, 3)
     
    finally:
        # Clean up
        if hwndDC:
            DeleteObject(hwndDC)
        if saveDC:
            DeleteObject(saveDC)
        if bmp:
            DeleteObject(bmp)
 

class FastScreenShot:

    def __init__(self, window_name, client=True):
        self.client = client
        self.hwnd = win32gui.FindWindow(None, window_name)
        self.rect = RECT()
        if client:
            GetClientRect(self.hwnd, ctypes.byref(self.rect))
        else:
            GetWindowRect(self.hwnd, ctypes.byref(self.rect))
        left, right, top, bottom = self.rect.left, self.rect.right, self.rect.top, self.rect.bottom
        self.w, self.h = right - left, bottom - top

        self.buffer_len = self.h * self.w * 4
        self.bmi = BITMAPINFO()
        self.bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        self.bmi.bmiHeader.biWidth = self.w
        self.bmi.bmiHeader.biHeight = -self.h  # Why minus? See [1]
        self.bmi.bmiHeader.biPlanes = 1  # Always 1
        self.bmi.bmiHeader.biBitCount = 32
        self.bmi.bmiHeader.biCompression = BI_RGB

        self.image = ctypes.create_string_buffer(self.buffer_len)
        self.image2 = ctypes.create_string_buffer(self.h * self.w * 3)

    def shoot(self):
        hwndDC = saveDC = bmp = None
        try:
            # Get device contexts
            hwndDC = GetWindowDC(self.hwnd)
            saveDC = CreateCompatibleDC(hwndDC)
            # Get bitmap
            bmp = CreateCompatibleBitmap(hwndDC, self.w, self.h)
            SelectObject(saveDC, bmp)
            if self.client:
                PrintWindow(self.hwnd, saveDC, 1)  # todo: result is never used??
            else:
                PrintWindow(self.hwnd, saveDC, 0)
            # Init bitmap info
            # Blit
            bits = windll.gdi32.GetDIBits(saveDC, bmp, 0, self.h, self.image, self.bmi, DIB_RGB_COLORS)
            assert bits == self.h
            # Replace pixels values: BGRX to RGB
            self.image2[0::3] = self.image[2::4]
            self.image2[1::3] = self.image[1::4]
            self.image2[2::3] = self.image[0::4]
             
            return bytes(self.image2), (self.w, self.h, 3)
         
        finally: # Clean up
            if hwndDC:
                DeleteObject(hwndDC)
            if saveDC:
                DeleteObject(saveDC)
            if bmp:
                DeleteObject(bmp)



def make_nd_array(c_pointer, shape, dtype=np.float64, order='C', own_data=True):
    arr_size = np.prod(shape[:]) * np.dtype(dtype).itemsize 
    if sys.version_info.major >= 3:
        buf_from_mem = ctypes.pythonapi.PyMemoryView_FromMemory
        buf_from_mem.restype = ctypes.py_object
        buf_from_mem.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
        buffer = buf_from_mem(c_pointer, arr_size, 0x100)
    else:
        buf_from_mem = ctypes.pythonapi.PyBuffer_FromMemory
        buf_from_mem.restype = ctypes.py_object
        buffer = buf_from_mem(c_pointer, arr_size)
    arr = np.ndarray(tuple(shape[:]), dtype, buffer, order=order)
    if own_data and not arr.flags.owndata:
        return arr.copy()
    else:
        return arr


def convert_nidhogg_screenshot_v1(im, shape):
    # im, shape = screenshot("Nidhogg", True)
    red_channel = np.frombuffer(np.array(im[0::3]), dtype=np.uint8)
    green_channel = np.frombuffer(np.array(im[1::3]), dtype=np.uint8)
    blue_channel = np.frombuffer(np.array(im[2::3]), dtype=np.uint8)
    mix = (0.3 * red_channel + 0.7 * green_channel + 0 * blue_channel)

    image = np.reshape(mix, (600, 800))
    image = image[::4, ::4]

    # cut out top for first version
    top_cut = int(image.shape[0] / 2)
    bottom_cut = int(image.shape[0] * 0.87)
    left_cut = 10
    right_cut = image.shape[1] - 10

    return image[top_cut:bottom_cut, left_cut:right_cut]


def convert_nidhogg_screenshot_v2(im, shape):
    image = np.reshape(np.frombuffer(np.array(im), dtype=np.uint8), (600, 800, 3))
    image = image[::4, ::4]

    # cut out top for first version
    top_cut = int(image.shape[0] / 2)
    bottom_cut = int(image.shape[0] * 0.87)
    left_cut = 10
    right_cut = image.shape[1] - 10

    return image[top_cut:bottom_cut, left_cut:right_cut]


def who_died_v2(image):
    bottom = image[image.shape[0]-2:]
    yellow = np.sum(bottom[:,:] == [255, 255, 0])
    orange = np.sum(bottom[:,:] == [255, 160, 64])
    if yellow + orange < 30:
        return 0
    if orange > yellow:  # orange blood, yellow scores
        return 1
    return -1  # yellow blood, orange scores


if __name__ == '__main__':
    fss = FastScreenShot("Nidhogg")

    # im, shape = fss.shoot()
    # image = convert_nidhogg_screenshot_v1(im, shape)
    # plt.imshow(image, cmap='gray')
    # plt.show()

    im, shape = fss.shoot()
    image = convert_nidhogg_screenshot_v2(im, shape)
    print(who_died_v2(image))
    print(image.shape)
    plt.imshow(image)
    plt.show()

