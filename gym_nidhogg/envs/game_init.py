import os
import subprocess
import time
import win32gui

from gym_nidhogg.envs import keyb


def press_and_release_key(key, rtime=0.1):
    keyb.SendInput(keyb.Keyboard(key))
    time.sleep(rtime)
    keyb.SendInput(keyb.Keyboard(key, flags=keyb.KEYEVENTF_KEYUP))


def reset_nidhogg():
    window = win32gui.FindWindow(None, "Nidhogg")
    win32gui.SetForegroundWindow(window)

    press_and_release_key(keyb.VK_ESCAPE, 0.2)
    press_and_release_key(keyb.VK_DOWN, 0.2)
    press_and_release_key(keyb.VK_RETURN, 0.2)
    time.sleep(0.3)
    press_and_release_key(keyb.VK_RETURN, 0.2)


def start_nidhogg():
    # open dxwnd
    work_dir = os.getcwd()
    os.chdir("e:\\CSIKI\\LINUX\\robotics\\dxwnd\\DxWnd\\")
    subprocess.Popen(["dxwnd.exe", "e:\\CSIKI\\GAMES\\Nidhogg\\Nidhogg.exe"])
    os.chdir(work_dir)  # change it back

    # choose nidhogg to run
    time.sleep(0.5)
    press_and_release_key(keyb.VK_RIGHT, 0.2)
    press_and_release_key(keyb.VK_MENU, 0.2)
    press_and_release_key(keyb.KEY_F, 0.2)
    press_and_release_key(keyb.VK_RETURN, 0.2)

    time.sleep(2)
    for i in range(7):
        press_and_release_key(keyb.VK_RETURN, 0.2)
        time.sleep(0.3)


def start_nidhogg_turbo_mode():
    # open dxwnd
    work_dir = os.getcwd()
    os.chdir("e:\\CSIKI\\LINUX\\robotics\\dxwnd\\DxWnd\\")
    subprocess.Popen(["dxwnd.exe", "e:\\CSIKI\\GAMES\\Nidhogg\\Nidhogg.exe"])
    os.chdir(work_dir)  # change it back

    # choose nidhogg to run
    time.sleep(0.5)
    press_and_release_key(keyb.VK_RIGHT, 0.2)
    press_and_release_key(keyb.VK_MENU, 0.2)
    press_and_release_key(keyb.KEY_F, 0.2)
    press_and_release_key(keyb.VK_RETURN, 0.2)

    # navigate in the nidhogg menu
    time.sleep(2)
    press_and_release_key(keyb.VK_RETURN, 0.2)
    #print('yeeee')
    time.sleep(0.5)
    press_and_release_key(keyb.VK_RETURN, 0.2)
    time.sleep(0.2)
    press_and_release_key(keyb.VK_RETURN, 0.2)
    time.sleep(0.2)
    press_and_release_key(keyb.VK_RETURN, 0.2) # now inside multiplayer

    time.sleep(0.3)
    press_and_release_key(keyb.VK_DOWN, 0.2)
    time.sleep(0.1)
    press_and_release_key(keyb.VK_DOWN, 0.2) # "variants" is now selected
    time.sleep(0.1)
    press_and_release_key(keyb.VK_RETURN, 0.2) # select "variants"
    time.sleep(0.3)

    for i in range(5):
        press_and_release_key(keyb.VK_UP, 0.2) # reach turbo mode
        time.sleep(0.1)
    press_and_release_key(keyb.VK_RETURN, 0.2) # toogle turbo mode

    press_and_release_key(keyb.VK_ESCAPE, 0.2) # back to menu
    time.sleep(0.1)
    press_and_release_key(keyb.VK_UP, 0.2)
    time.sleep(0.1)
    press_and_release_key(keyb.VK_UP, 0.2) # selection on multiplayer
    time.sleep(0.1)
    for i in range(2):
        press_and_release_key(keyb.VK_RETURN, 0.2) # go in game
        time.sleep(0.2)


if __name__ == '__main__':
    start_nidhogg_turbo_mode()
    #reset_nidhogg()
