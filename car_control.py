##
## EPITECH PROJECT, 2025
## vroom
## File description:
## main
##

import curses
from pyvesc.VESC import VESC

MAX_SPEED = 0.05
MIN_SPEED = -0.05
SPEED_STEP = 0.01

MAX_STEERING = 1.0
MIN_STEERING = 0.0
STEERING_STEP = 0.05

def main(stdscr):
    curses.cbreak()
    stdscr.nodelay(True)
    stdscr.keypad(True)
    stdscr.clear()
    stdscr.addstr("Use UP/DOWN arrows to control speed, LEFT/RIGHT to steer. Press 'q' to quit.\n")

    vesc = VESC(serial_port='/dev/ttyACM0')
    speed = 0.0
    steering = 0.5

    try:
        while True:
            key = stdscr.getch()

            if key == curses.KEY_UP:
                speed = min(speed + SPEED_STEP, MAX_SPEED)
            elif key == curses.KEY_DOWN:
                speed = max(speed - SPEED_STEP, MIN_SPEED)
            elif key == curses.KEY_RIGHT:
                steering = min(steering + STEERING_STEP, MAX_STEERING)
            elif key == curses.KEY_LEFT:
                steering = max(steering - STEERING_STEP, MIN_STEERING)
            elif key == ord('q'):
                break

            vesc.set_duty_cycle(speed)
            vesc.set_servo(steering)

            stdscr.addstr(2, 0, f"Speed: {speed:.3f} | Steering: {steering:.2f}      ")
            stdscr.refresh()
            curses.napms(50)

    finally:
        vesc.set_duty_cycle(0)
        vesc.set_servo(0.5)
        stdscr.addstr(4, 0, "Exiting safely...\n")
        stdscr.refresh()
        curses.napms(1000)

curses.wrapper(main)

