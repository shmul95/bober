
import os
import time
import json
import numpy as np
import pygame
from collections import deque
from pyvesc.VESC import VESC
from autopilot import get_action 

# === [MODIFIED] === Additional Imports ===
import math
import matplotlib.pyplot as plt
import pandas as pd

# --- Constantes Manette ---
BUTTON_A = 0
BUTTON_B = 1
BUTTON_X = 2
BUTTON_Y = 3

AXIS_STEER = 0
AXIS_LT    = 2
AXIS_RT    = 5

MAX_SPEED      = 0.30
REVERSE_SPEED  = -0.05
STEERING_CENTER = 0.5
STEERING_RANGE  = 1.0
STEERING_OFFSET = -0.05

# === [MODIFIED] === Steering Angle Parameters ===
MAX_STEERING_ANGLE = math.radians(30)  # 30 degrees in radians

# --- Constantes Autopilot ---
ACTION_CFG_PATH = "action_config.json"
NB_RAYCAST      = 40

def load_config():
    with open(ACTION_CFG_PATH) as f:
        return json.load(f)

# === [MODIFIED] === Coordinate system initialization ===
x, y = 0.0, 0.0
theta = 0.0
track = []  # Will hold (x, y, timestamp)
last_time = time.time()

def update_position(x, y, theta, speed, steer, dt):
    steering_bias = 30
    steer_angle = (steer - 0.5) * 2 * MAX_STEERING_ANGLE
    dx = speed * math.cos(theta) * dt
    dy = speed * math.sin(theta) * dt
    dtheta = math.tan(steer_angle) * speed * dt * steering_bias  # simplified kinematics
    x += dx
    y += dy
    theta += dtheta
    return x, y, theta

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
        # === [MODIFIED] === Real-time delta calculation ===
        now = time.time()
        dt = now - last_time
        last_time = now

        # — gestion des événements —
        for event in pygame.event.get():
            # print(f"{event=}")
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == BUTTON_B:
                    is_autopilot = not is_autopilot
                    mode = "AUTOPILOT" if is_autopilot else "MANUEL"
                    print(f"🔄 Passage en mode {mode}")
                elif event.button == BUTTON_Y:
                    if track:
                        df = pd.DataFrame(track, columns=["x", "y", "timestamp"])
                        plt.plot(df["x"], df["y"], marker='o')
                        plt.title("Trajectoire")
                        plt.xlabel("x")
                        plt.ylabel("y")
                        plt.axis("equal")
                        plt.grid(True)
                        plt.savefig("plot.png")
                        plt.close()
                        print("📸 Trajectory saved to plot.png")
                elif event.button == BUTTON_X:
                    print("🗑️ Reset triggered via window X")
                    x, y, theta = 0.0, 0.0, 0.0
                    track.clear()
                    last_time = time.time()


        cfg_mtime = os.path.getmtime(ACTION_CFG_PATH)
        if cfg_mtime != last_cfg_mtime:
            cfg = load_config()
            vision_hist = deque(maxlen=cfg["HISTORY_SIZE"])
            last_cfg_mtime = cfg_mtime
            print("🔄 Config autopilot rechargée")

        if is_autopilot:
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

            # === [MODIFIED] === Update and log coordinates in autopilot ===
            sim_speed = np.interp(speed, [REVERSE_SPEED, MAX_SPEED], [-1, 1])
            sim_steer = np.clip(steer, 0.0, 1.0)
            x, y, theta = update_position(x, y, theta, sim_speed, sim_steer, dt)
            track.append((x, y, now))
            print(f"📍 Pos: ({x:.2f}, {y:.2f}) | θ: {math.degrees(theta):.1f}°")

        else:
            steer_in = joy.get_axis(AXIS_STEER)
            steering = STEERING_CENTER + steer_in * STEERING_RANGE/2
            steering = np.clip(steering, 0.0, 1.0)

            lt = joy.get_axis(AXIS_LT)
            if lt != -1.0:
                speed = (lt + 1)* (REVERSE_SPEED/2)
            else:
                rt = joy.get_axis(AXIS_RT)
                speed = (rt + 1)* (MAX_SPEED/2)

            vesc.set_servo(steering + STEERING_OFFSET)
            vesc.set_duty_cycle(speed)
            # print(f"[MAN] {steering=:.2f} | {speed=:.3f}")

            # === [MODIFIED] === Update and log coordinates in manual mode ===
            # sim_speed = np.interp(speed, [REVERSE_SPEED, MAX_SPEED], [-1, 1])
            # sim_steer = np.clip(steering, 0.0, 1.0)
            x, y, theta = update_position(x, y, theta, speed, steering, dt)
            track.append((x, y, now))
            # print(f"📍 Pos: ({x:.2f}, {y:.2f}) | θ: {math.degrees(theta):.1f}°")

        time.sleep(0.01)

except KeyboardInterrupt:
    pass

finally:
    vesc.set_duty_cycle(0)
    vesc.set_servo(0.5)
    pygame.quit()
    print("✅ Arrêt propre")

