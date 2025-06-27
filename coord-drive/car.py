import os
import time
import json
import numpy as np
import pygame
from collections import deque
from pyvesc.VESC import VESC
from autopilot import get_action 

# --- Constantes Manette ---
BUTTON_B = 1            # vérifiez avec un print(event.button) si besoin
AXIS_STEER = 0
AXIS_LT    = 2
AXIS_RT    = 5

MAX_SPEED      = 0.30
REVERSE_SPEED  = -0.05
STEERING_CENTER = 0.5
STEERING_RANGE  = 1.0
STEERING_OFFSET = -0.2

# --- Constantes Autopilot ---
ACTION_CFG_PATH = "action_config.json"
NB_RAYCAST      = 40

def load_config():
    with open(ACTION_CFG_PATH) as f:
        return json.load(f)

# --- Initialisation ---
pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("Pas de joystick détecté.")
    exit()
joy = pygame.joystick.Joystick(0)
joy.init()

vesc = VESC(serial_port="/dev/ttyACM0")
is_autopilot   = False
is_reversing   = False
cfg            = load_config()
vision_hist    = deque(maxlen=cfg["HISTORY_SIZE"])
last_cfg_mtime = os.path.getmtime(ACTION_CFG_PATH)
last_dist_mtime= 0
last_vis       = None

print("Appuyez sur B pour basculer MANUEL ↔ AUTOPILOT")

try:
    while True:
        # — gestion des événements —
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
            if event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_B:
                is_autopilot = not is_autopilot
                mode = "AUTOPILOT" if is_autopilot else "MANUEL"
                print(f"🔄 Passage en mode {mode}")

        cfg_mtime = os.path.getmtime(ACTION_CFG_PATH)
        if cfg_mtime != last_cfg_mtime:
            cfg = load_config()
            vision_hist = deque(maxlen=cfg["HISTORY_SIZE"])
            last_cfg_mtime = cfg_mtime
            print("🔄 Config autopilot rechargée")

        if is_autopilot:
            # — lecture distances (comme dans autopilot.py) —
            dist_file = os.path.join("camera", "cam_mask", "distance.txt")
            if os.path.exists(dist_file):
                mtime = os.path.getmtime(dist_file)
                if mtime != last_dist_mtime:
                    last_dist_mtime = mtime
                    with open(dist_file) as f:
                        parts = [float(x) for x in f.read().split(",") if x]
                    if len(parts) == NB_RAYCAST:
                        last_vis = np.array(parts, dtype=np.float32)
                    else:
                        print(f"⚠️ attendu {NB_RAYCAST} valeurs, reçu {len(parts)}")
            action, is_reversing = get_action(last_vis, cfg, is_reversing)
            speed, steer = action[0]
            servo_cmd = (-steer)/2 + 0.5
            speed_cmd = np.clip(speed, 0.02, 0.03)
            vesc.set_servo(servo_cmd)
            vesc.set_duty_cycle(speed_cmd)
            print(f"[AP] speed={speed_cmd:.3f} servo={servo_cmd:.3f}")

        else:
            # — mode manuel —
            steer_in = joy.get_axis(AXIS_STEER)
            steering = STEERING_CENTER + steer_in * STEERING_RANGE/2
            steering += STEERING_OFFSET
            steering = np.clip(steering, 0.0, 1.0)

            lt = joy.get_axis(AXIS_LT)
            if lt != -1.0:
                speed = (lt + 1)* (REVERSE_SPEED/2)
            else:
                rt = joy.get_axis(AXIS_RT)
                speed = (rt + 1)* (MAX_SPEED/2)

            vesc.set_servo(steering)
            vesc.set_duty_cycle(speed)
            print(f"[MAN] {steering=:.2f} | {speed=:.3f}")

        time.sleep(0.01)

except KeyboardInterrupt:
    pass

finally:
    vesc.set_duty_cycle(0)
    vesc.set_servo(0.5)
    pygame.quit()
    print("✅ Arrêt propre")
