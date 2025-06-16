import depthai as dai
import cv2
import os
from datetime import datetime
from sys import argv
import pygame
from pyvesc.VESC import VESC
import time

# --- DepthAI Camera Setup ---
pipeline = dai.Pipeline()

cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setFps(2)

xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("rgb")
cam_rgb.preview.link(xout.input)

os.makedirs("data", exist_ok=True)

# --- Gamepad & VESC Setup ---
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick connected.")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

vesc = VESC(serial_port="/dev/ttyACM0")

MAX_SPEED = 0.05
REVERSE_SPEED = -0.025
STEERING_CENTER = 0.5
STEERING_RANGE = 1

BUTTON_A = 1
BUTTON_B = 2
BUTTON_RB = 5

activated = True
preserve = False

pygame.display.set_caption("Gamepad Control")

# --- Main Loop ---
with dai.Device(pipeline) as device:
    q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    frame_count = 0

    try:
        while True:
            frame = q_rgb.get().getCvFrame()

            if preserve:
                filename = datetime.now().strftime("data/frame_%Y%m%d_%H%M%S_%f.png")
            else:
                filename = "data/frame.png"

            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
            frame_count += 1

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

                if joystick.get_button(BUTTON_RB):
                    speed = REVERSE_SPEED
                else:
                    rt_input = joystick.get_axis(5)
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

