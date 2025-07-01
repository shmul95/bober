import time
import numpy as np
import pygame
from pyvesc.VESC import VESC
import csv

# === Config manette & VESC ===
R2_AXIS = 5
L2_AXIS = 2
nb_raycast = 40  # nombre de raycasts fictifs

MAX_SPEED = 0.2
REVERSE_SPEED = -0.05
STEERING_CENTER = 0.5
STEERING_RANGE = 1.0

BUTTON_A = 0
BUTTON_B = 1
BUTTON_R1 = 5  # boost toggle

# === Variables dynamiques ===
current_speed = 0.0
steering = 0.0
braking = 0
boost_mode = False

# === Initialisation ===
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Aucune manette détectée.")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"🎮 Manette détectée : {joystick.get_name()}")

vesc = VESC(serial_port="/dev/ttyACM0")

# Ouvre le fichier CSV pour écrire les données
csv_file = open("data/driving_data.csv", mode="w", newline="", buffering=1)
csv_writer = csv.writer(csv_file)
# En-tête
csv_writer.writerow([f"ray_{i}" for i in range(nb_raycast)] + ["speed", "steering", "brake"])

def compress_rays(ray_list, x_max=94.0, a=1, min_threshold=80.0):
    return [
        0.0 if x <= min_threshold else ((x - min_threshold) / (x_max - min_threshold)) ** a
        for x in ray_list
    ]

def get_action():
    global steering
    return np.array([[current_speed, steering]], dtype=np.float32)

try:
    prev_button_r1 = False
    prev_button_a = False
    prev_button_b = False
    
    print("🚗 Contrôle manuel IRL démarré.")
    while True:
        pygame.time.Clock().tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt

        button_r1 = joystick.get_button(BUTTON_R1)
        button_a = joystick.get_button(BUTTON_A)
        button_b = joystick.get_button(BUTTON_B)
        
        # Toggle boost (click R1)
        if prev_button_r1 and not button_r1:
            boost_mode = not boost_mode
            print("⚡ Boost mode :", boost_mode)

        speed_max = 0.1 if boost_mode else MAX_SPEED

        # Lecture de l'axe R2 (valeurs de 0.0 à 1.0)
        r2_value = joystick.get_axis(R2_AXIS)

        # Seuil minimal pour activer l'accélération
        if r2_value > 0.05:
            current_speed = min(speed_max, r2_value * speed_max)
            braking = 0
            print("🟢 Accélération R2 →", current_speed)
        else:
            # current_speed = max(0.0, current_speed - 0.01)
            braking = 1
            print("⚠️ Frein moteur     →", current_speed)

        # Frein (L2 enfoncé) = arrêt + désactive boost
        if joystick.get_axis(L2_AXIS) > 0.1:
            current_speed = 0.05
            braking = 1
            boost_mode = False
            print("⏹️ Arrêt (L2 enfoncé)")

        if prev_button_a and not button_a:
            current_speed = min(speed_max, current_speed + 0.05)
            braking = 0
            print("🟢 Accélération clic →", current_speed)

        # Frein par clic B
        if prev_button_b and not button_b:
            current_speed = max(0.0, current_speed - 0.05)
            print("🔴 Freinage clic     →", current_speed)
        prev_button_r1 = button_r1

        # Steering
        steering = joystick.get_axis(0)

        action = get_action()
        speed_val = action[0][0]
        steering_val = action[0][1]

        # Map steering [-1,1] → servo [0,1]
        servo_cmd = STEERING_CENTER + (steering_val * STEERING_RANGE / 2)
        servo_cmd = max(0.0, min(1.0, servo_cmd))

        vesc.set_servo(servo_cmd)
        vesc.set_duty_cycle(speed_val)

        try:
            with open("camera/data/distance.txt", "r") as f:
                line = f.readline().strip()
                raycast_data = [float(x) for x in line.split(",")]
                # Si moins de nb_raycast valeurs, compléte avec des 0
                if len(raycast_data) < nb_raycast:
                    raycast_data += [0.0] * (nb_raycast - len(raycast_data))
                # Si plus, coupe à nb_raycast
                raycast_data = raycast_data[:nb_raycast]
        except Exception as e:
            print(f"Erreur lecture distance.txt: {e}")
            raycast_data = [0.0] * nb_raycast

        # print(raycast_data)
        raycast_data = compress_rays(raycast_data)
        # Écrit dans le CSV
        csv_writer.writerow(raycast_data + [speed_val, steering_val, braking])

        print(f"🚗 Duty: {speed_val:.3f} | Servo: {servo_cmd:.2f} | Boost: {boost_mode} | Brake: {braking}")
        prev_button_r1 = button_r1
        prev_button_a = button_a
        prev_button_b = button_b
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n⛔ Arrêt manuel.")
finally:
    vesc.set_duty_cycle(0)
    vesc.set_servo(STEERING_CENTER)
    csv_file.close()
    pygame.quit()
    print("✅ Fermeture propre.")
