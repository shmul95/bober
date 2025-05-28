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

STEERING_CENTER = 0.5
STEERING_RANGE = 0.5
BUTTON_A = 1
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
            # 🕹️ Use left analog stick (axis 0) for steering
            steer_input = joystick.get_axis(0)  # -1 (left) to 1 (right)
            steering = STEERING_CENTER + (steer_input * STEERING_RANGE / 2)
            steering = max(0.0, min(1.0, steering))

            # Optional: throttle with axis 1
            throttle_input = -joystick.get_axis(1)  # up is negative
            speed = throttle_input * 0.05
            vesc.set_duty_cycle(speed)

            # Send steering
            vesc.set_servo(steering)
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

