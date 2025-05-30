import cv2
import os
from datetime import datetime
from sys import argv
import pygame
from pyvesc.VESC import VESC
import time

# --- Gamepad & VESC Setup ---
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick connected.")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

vesc = VESC(serial_port="/dev/ttyACM0")

MAX_SPEED = 0.20
REVERSE_SPEED = -0.05
STEERING_CENTER = 0.49
STEERING_RANGE = 1

BUTTON_A = 1
BUTTON_B = 2
BUTTON_LB = 4
BUTTON_RB = 5
BUTTON_LT = 2
BUTTON_RT = 5

activated = True
preserve = False

pygame.display.set_caption("Gamepad Control")

# --- Main Loop ---
try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
            elif event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_B:
                preserve = not preserve
                print("preserve" if preserve else "not preserve")
            elif event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_A:
                activated = not activated
                print("autonomous" if activated else "not autonomous")
        if activated:
            steer_input = joystick.get_axis(0)
            steering = STEERING_CENTER + (steer_input * STEERING_RANGE / 2)
            steering = max(0.0, min(1.0, steering))
            lt_input = joystick.get_axis(BUTTON_LT)
            if lt_input != -1:
                speed = (lt_input + 1) * (REVERSE_SPEED / 2)
            else:
                rt_input = joystick.get_axis(BUTTON_RT)
                speed = (rt_input + 1) * (MAX_SPEED / 2)
            vesc.set_servo(steering)
            vesc.set_duty_cycle(speed)
            print(f"Steering: {steering:.2f} | Speed: {speed:.3f}")
        else:
            vesc.set_duty_cycle(0)
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
finally:
    vesc.set_duty_cycle(0)
    vesc.set_servo(0.5)
    pygame.quit()
