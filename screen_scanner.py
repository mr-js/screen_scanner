import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui
import pygetwindow as gw
import time

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
    for coord in enemies.values():
        if (abs(new_coord[0] - coord[0]) <= search_radius) and (abs(new_coord[1] - coord[1]) <= search_radius):
            return True
    return False

def scan_for_enemies(threshold=0.8, search_radius=20):
    print('Scan for enemies...')
    screen_gray, screen_width, screen_height = capture_screen()
    enemy_template = load_template('enemy_template.png')
    
    found = None
    scales = np.linspace(0.5, 1.5, 20)  # Масштабы от 50% до 150%
    
    for scale in scales:
        resized_template = cv2.resize(enemy_template, (0, 0), fx=scale, fy=scale)
        if resized_template.shape[0] > screen_gray.shape[0] or resized_template.shape[1] > screen_gray.shape[1]:
            continue
        
        res = cv2.matchTemplate(screen_gray, resized_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        if found is None or max_val > found[0]:
            found = (max_val, max_loc, scale, resized_template.shape)

    if found and found[0] >= threshold:
        max_val, max_loc, scale, template_shape = found
        top_left = max_loc
        bottom_right = (top_left[0] + template_shape[1], top_left[1] + template_shape[0])
        cv2.rectangle(screen_gray, top_left, bottom_right, (0, 255, 0), 2)
        
        bottom_left = (bottom_right[0], top_left[1] + template_shape[0])
        
        offset_x = -search_radius  # Отступ влево
        offset_y = search_radius   # Отступ вниз
        
        click_x = int((bottom_left[0] + offset_x) * screen_width / screen_gray.shape[1])
        click_y = int((bottom_left[1] + offset_y) * screen_height / screen_gray.shape[0])
        
        attack(click_x, click_y)
        
        max_display_width = 800  # or other desired value
        max_display_height = 600  # or other desired value
        screen_gray_resized = resize_image(screen_gray, max_display_width, max_display_height)
        
        # cv2.imshow('Detected Enemies', screen_gray_resized)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
        return (bottom_left, (click_x, click_y))
    
    else:
        return None

def attack(click_x, click_y):
    print('Attacking the enemy...')
    pyautogui.doubleClick(click_x, click_y)
    time.sleep(2)  # Подождать 3 секунды

def battle():
    print('Make battle...')
    time.sleep(1)
    pyautogui.press('i')
    time.sleep(0.25)
    pyautogui.press('enter')
    time.sleep(0.5)
    pyautogui.press('esc')
    time.sleep(1)

def recurrent():
    print('Recurrent units...')
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

def quicksave_load():
    print('Loading quicksave...')
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(1)
    pyautogui.press('esc')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(0.5)
    pyautogui.press('tab')
    time.sleep(0.5)

def find_disciples_window():
    print('Finding game...')
    disciples_window = gw.getWindowsWithTitle('Disciples II')[0]
    return disciples_window

def main():
    disciples_window = find_disciples_window()
    if not disciples_window.isActive:
        disciples_window.activate()
        time.sleep(1)
        quicksave_load()
    
        enemies = {}
        search_radius = 20
        
        while True:
            result = scan_for_enemies(threshold=0.4, search_radius=search_radius)
            
            if result:
                bottom_left, click_coords = result
                
                if not is_near_existing_enemies(bottom_left, enemies, search_radius):
                    enemies[bottom_left] = click_coords
                    battle()
                    recurrent()
            else:
                break
    
    print('Finished')

if __name__ == "__main__":
    main()
