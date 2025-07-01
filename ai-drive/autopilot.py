import time
import numpy as np
import joblib
import pygame
from pyvesc.VESC import VESC

# === Paramètres ===
nb_raycast = 40
MAX_SPEED = 0.05  # duty_cycle max
STEERING_CENTER = 0.5
STEERING_RANGE = 1.0
def compress_rays(ray_list, x_max=94.0, a=1, min_threshold=80.0):
    return [
        0.0 if x <= min_threshold else ((x - min_threshold) / (x_max - min_threshold)) ** a
        for x in ray_list
    ]
# === Initialisation manette & VESC ===
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick connected.")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

vesc = VESC(serial_port="/dev/ttyACM0")

# === Modèle ===
model = joblib.load("model/driving_model_lgbm.pkl")
scaler_X = joblib.load("model/scaler_X.save")

# === Boucle principale ===
try:
    autonomous = True
    BUTTON_A = 1  # Activer / désactiver autopilot

    print("🚗 Autopilot IRL LGBM lancé.")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_A:
                autonomous = not autonomous
                print("🔁 Autopilot activé" if autonomous else "🕹️ Mode manuel")

        if autonomous:
            # === Lire les raycasts depuis fichier
            try:
                with open("camera/data/distance.txt", "r") as f:
                    line = f.readline().strip()
                    ray_values = [int(x) for x in line.split(",") if x.strip()]
                if len(ray_values) < nb_raycast:
                    ray_values += [0] * (nb_raycast - len(ray_values))
                ray_values = ray_values[:nb_raycast]
            except Exception as e:
                print("Erreur lecture raycasts :", e)
                continue
            ray_values = compress_rays(ray_values)
            # === Utilisation directe des valeurs
            print("Ray values (raw):", ray_values)
            X = np.array(ray_values).reshape(1, -1)
            X_scaled = scaler_X.transform(X)

            # === Prédiction
            brake_pred, speed_pred, steering_pred = model.predict(X_scaled)[0]

            # === Application du frein
            if brake_pred > 0.5 and speed_pred > 0.1:
                duty = 0.0
                print("🟥 Freinage activé")
            else:
                duty = max(speed_pred, 0.01)
                duty = min(duty, MAX_SPEED)

            # === Mapping direction [-1,1] → servo [0,1]
            steering = STEERING_CENTER + (steering_pred * STEERING_RANGE / 2)
            steering = max(0.0, min(1.0, steering))

            # === Envoi aux moteurs
            vesc.set_servo(steering)
            vesc.set_duty_cycle(duty)

            print(f"🔮 Speed: {duty:.3f} | Steering: {steering:.2f} | Break: {brake_pred:.2f}")

        else:
            # Mode manuel → arrêt du moteur
            vesc.set_duty_cycle(0)

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n⛔ Arrêt manuel.")
finally:
    vesc.set_duty_cycle(0)
    vesc.set_servo(STEERING_CENTER)
    pygame.quit()
    print("✅ Fermeture propre.")
