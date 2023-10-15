import time
import win32gui

from PIL import ImageOps, Image, ImageGrab
from numpy import *
import time
import cv2
import win32gui


WINDOW_SUBSTRING = "Asterios"


# Brazenhem algo
def draw_line(x1=0, y1=0, x2=0, y2=0):

    coordinates = []

    dx = x2 - x1
    dy = y2 - y1

    sign_x = 1 if dx > 0 else -1 if dx < 0 else 0
    sign_y = 1 if dy > 0 else -1 if dy < 0 else 0

    if dx < 0:
        dx = -dx
    if dy < 0:
        dy = -dy

    if dx > dy:
        pdx, pdy = sign_x, 0
        es, el = dy, dx
    else:
        pdx, pdy = 0, sign_y
        es, el = dx, dy

    x, y = x1, y1

    error, t = el / 2, 0

    coordinates.append([x, y])

    while t < el:
        error -= es
        if error < 0:
            error += el
            x += sign_x
            y += sign_y
        else:
            x += pdx
            y += pdy
        t += 1
        coordinates.append([x, y])

    return coordinates


# Smooth move mouse from current pos to xy
def smooth_move(autohotpy, x, y):
    flags, hcursor, (startX, startY) = win32gui.GetCursorInfo()
    coordinates = draw_line(startX, startY, x, y)
    x = 0
    for dot in coordinates:
        x += 1
        if x % 2 == 0 and x % 3 == 0:
            time.sleep(0.01)
        autohotpy.moveMouseToPosition(dot[0], dot[1])


def get_window_info():
    # set window info
    window_info = {}
    win32gui.EnumWindows(set_window_coordinates, window_info)
    return window_info


# EnumWindows handler
# sets L2 window coordinates
def set_window_coordinates(hwnd, window_info):
    if win32gui.IsWindowVisible(hwnd):
        if WINDOW_SUBSTRING in win32gui.GetWindowText(hwnd):
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[0]
            y = rect[1]
            w = rect[2] - x
            h = rect[3] - y
            window_info['x'] = x
            window_info['y'] = y
            window_info['width'] = w
            window_info['height'] = h
            window_info['name'] = win32gui.GetWindowText(hwnd)
            win32gui.SetForegroundWindow(hwnd)


def get_screen(x1, y1, x2, y2):
    box = (x1 + 8, y1 + 30, x2 - 8, y2)
    screen = ImageGrab.grab(box)
    img = array(screen.getdata(), dtype=uint8).reshape((screen.size[1], screen.size[0], 3))
    return img


def get_target_centers(img):

    # Hide buff line
    # img[0:70, 0:500] = (0, 0, 0)

    # Hide your name in first camera position (default)
    img[210:230, 350:440] = (0, 0, 0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('1_gray_img.png', gray)

    # Find only white text
    ret, threshold1 = cv2.threshold(gray, 252, 255, cv2.THRESH_BINARY)
    cv2.imwrite('2_threshold1_img.png', threshold1)

    # Morphological transformation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 5))
    closed = cv2.morphologyEx(threshold1, cv2.MORPH_CLOSE, kernel)
    cv2.imwrite('3_morphologyEx_img.png', closed)
    closed = cv2.erode(closed, kernel, iterations=1)
    cv2.imwrite('4_erode_img.png', closed)
    closed = cv2.dilate(closed, kernel, iterations=1)
    cv2.imwrite('5_dilate_img.png', closed)

    centers, _ = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return centers
