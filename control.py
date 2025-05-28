#!/usr/bin/env python3
import pygame

pygame.init()
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    done = True
else:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
BUTTON_A = 1
activated = False
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Test")
done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                if event.value < -0.5:
                    print("Tourner à gauche")
                elif event.value > 0.5:
                    print("Tourner à droite")
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == BUTTON_A:
                activated = not activated
                if activated:
                    print("Activé!")
                else:
                    print("Désactivé!")
        if activated:
            pass
pygame.quit()
