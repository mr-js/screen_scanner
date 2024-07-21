import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui
import pygetwindow as gw
import time
import os


DEMO = False
QUICKSAVE_RELOAD = False


def capture_screen():
    screen = ImageGrab.grab()
    screen_np = np.array(screen)
    screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)
    return screen_gray, screen_np.shape[1], screen_np.shape[0]


def load_template(template_path):
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise ValueError(f"Template image at path {template_path} could not be loaded.")
    return template


def resize_image(image, max_width, max_height):
    h, w = image.shape[:2]
    if w > max_width or h > max_height:
        scaling_factor = min(max_width / w, max_height / h)
        new_size = (int(w * scaling_factor), int(h * scaling_factor))
        resized_image = cv2.resize(image, new_size)
        return resized_image
    return image


def is_near_existing_enemies(new_coord, enemies, search_radius):
    for coord in enemies:
        if (abs(new_coord[0] - coord[0]) <= search_radius) and (abs(new_coord[1] - coord[1]) <= search_radius):
            return True
    return False


def scan_for_enemies(scale, threshold, search_radius, borders):
    # scales = np.linspace(0.5, 1.5, 20)
    print('Scan for enemies...')
    screen_gray, screen_width, screen_height = capture_screen()
    enemy_templates = dict()
    
    for file in os.listdir('enemy_templates'):
        enemy_templates[file] = load_template(os.path.join('enemy_templates', file))
    
    all_enemies = []

    for enemy_template in enemy_templates.keys():
        found_enemies = []
        resized_template = cv2.resize(enemy_templates[enemy_template], (0, 0), fx=scale, fy=scale)
        if resized_template.shape[0] > screen_gray.shape[0] or resized_template.shape[1] > screen_gray.shape[1]:
            continue
        
        res = cv2.matchTemplate(screen_gray, resized_template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        
        for pt in zip(*loc[::-1]):
            top_left = pt
            bottom_right = (top_left[0] + resized_template.shape[1], top_left[1] + resized_template.shape[0])
            cv2.rectangle(screen_gray, top_left, bottom_right, (0, 255, 0), 2)
            
            bottom_left = (bottom_right[0], top_left[1] + resized_template.shape[0])
            offset_x = -search_radius
            offset_y = search_radius
            click_x = int((bottom_left[0] + offset_x) * screen_width / screen_gray.shape[1])
            click_y = int((bottom_left[1] + offset_y) * screen_height / screen_gray.shape[0])

            if borders[0] <= click_x <= (borders[0] + borders[2]) and borders[1] <= click_y <= (borders[1] + borders[3]):
                enemy = (click_x, click_y)
                if not is_near_existing_enemies(enemy, found_enemies, search_radius):
                    found_enemies.append(enemy)
        
        all_enemies.append({enemy_template: found_enemies})

    if DEMO:
        max_display_width = 1920
        max_display_height = 1080
        # screen_gray_resized = resize_image(screen_gray, max_display_width, max_display_height)
        # cv2.imshow('Detected Enemies', screen_gray_resized)
        cv2.imshow('Detected Enemies', screen_gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return all_enemies


def attack(enemy):
    print('Attacking the enemy...')
    click_x, click_y = enemy
    pyautogui.doubleClick(click_x, click_y)
    
    time.sleep(4)

    print('Make battle...')
    time.sleep(1)
    pyautogui.press('i')
    time.sleep(0.25)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('esc')
    
    time.sleep(0.5)
    for _ in range(10):
        pyautogui.typewrite(['enter'])
        time.sleep(0.25)

    print('After battle...')
    pyautogui.typewrite(['enter'])
    pyautogui.typewrite('LIFEISACARNIVAL')
    pyautogui.typewrite(['enter'])
    pyautogui.typewrite(['esc'])
    pyautogui.typewrite(['enter'])
    pyautogui.typewrite('HELP!')
    pyautogui.typewrite(['enter'])
    pyautogui.typewrite(['esc'])
    pyautogui.typewrite(['enter'])
    pyautogui.typewrite('BORNTORUN')
    pyautogui.typewrite(['enter'])
    pyautogui.typewrite(['esc'])
    pyautogui.typewrite('m')

    time.sleep(1)
    
    print('Attacked OK')


def quicksave_load():
    print('Loading quicksave...')
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(2)
    pyautogui.press('esc')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)


def find_window(windows_title):
    print('Finding game...')
    window = gw.getWindowsWithTitle(windows_title)[0]
    return window


def main():
    scale=0.6
    threshold=0.6
    search_radius = 20
    max_enemies = 64
    killed_ememies = 0
    window = find_window('Disciples II')
    if not window.isActive:
        window.activate()     
        time.sleep(1)
        if QUICKSAVE_RELOAD:
            quicksave_load()
        enemies = set()
        while True:
            detected_enemies = scan_for_enemies(scale, threshold, search_radius, borders=(window.left, window.top, window.width, window.height))
            print(f'Detected: {detected_enemies}')
            if DEMO:
                break
            all_enemies = [coordinate for template in detected_enemies for coordinates in template.values() for coordinate in coordinates]
            if not all_enemies or killed_ememies >= max_enemies:
                break
            if all_enemies:
                for enemy in all_enemies:
                    print(f'Attacted: {enemy}')
                    attack(enemy)
                    killed_ememies += 1
                    print(f'{killed_ememies=}')

    print('Finished')


if __name__ == "__main__":
    main()
