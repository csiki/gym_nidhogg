import os
import subprocess
import keyb
import time
import win32gui


def press_and_release_key(key, rtime=0.1):
    keyb.SendInput(keyb.Keyboard(key))
    time.sleep(rtime)
    keyb.SendInput(keyb.Keyboard(key, flags=keyb.KEYEVENTF_KEYUP))


def reset_nidhogg():
    window = win32gui.FindWindow(None, "Nidhogg")
    win32gui.SetForegroundWindow(window)

    press_and_release_key(keyb.VK_ESCAPE)
    press_and_release_key(keyb.VK_DOWN)
    press_and_release_key(keyb.VK_RETURN)
    time.sleep(0.3)
    press_and_release_key(keyb.VK_RETURN)


def start_nidhogg():
    # open dxwnd
    os.chdir("e:\\CSIKI\\LINUX\\dxwnd\\DxWnd\\")
    subprocess.Popen(["dxwnd.exe", "e:\\CSIKI\\GAMES\\Nidhogg\\Nidhogg.exe"])

    # choose nidhogg to run
    time.sleep(0.5)
    press_and_release_key(keyb.VK_RIGHT)
    press_and_release_key(keyb.VK_MENU)
    press_and_release_key(keyb.KEY_F)
    press_and_release_key(keyb.VK_RETURN)

    # navigate in the nidhogg menu
    time.sleep(2)
    for i in range(6):
        press_and_release_key(keyb.VK_RETURN)
        time.sleep(0.5)


if __name__ == '__main__':
    #start_nidhogg()
    reset_nidhogg()
