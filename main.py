import pygame
from pyvesc.VESC import VESC
import time

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
BUTTON_RB = 5

activated = True

screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Gamepad Control")

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
            elif event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_A:
                activated = not activated
                print("Activé!" if activated else "Désactivé!")

        if activated:
            steer_input = joystick.get_axis(0)
            steering = STEERING_CENTER + (steer_input * STEERING_RANGE / 2)
            steering = max(0.0, min(1.0, steering))

            if event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_RB:
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

