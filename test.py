import pyautogui
import pygetwindow as gw
import time

def find_disciples_window():
    print('Finding game...')
    disciples_window = gw.getWindowsWithTitle('Scenario Editor')[0]
    return disciples_window


disciples_window = find_disciples_window()
if not disciples_window.isActive:
    disciples_window.activate()
    # time.sleep(1)
    print('Adding items...')
    for x in range(1):
        pyautogui.click(350, 480)
        if x > 0:
            pyautogui.click(640, 610)
        pyautogui.click(550, 650)