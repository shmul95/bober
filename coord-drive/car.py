
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
BUTTON_LB = 4
BUTTON_RB = 5

AXIS_STEER = 0
AXIS_LT    = 2
AXIS_RT    = 5

MAX_SPEED      = 0.15
REVERSE_SPEED  = -0.025
STEERING_CENTER = 0.5
STEERING_RANGE  = 1.0
STEERING_OFFSET = 0

# === [MODIFIED] === Steering Angle Parameters ===
MAX_STEERING_ANGLE = np.radians(30)  # 30 degrees in radians
WHEELBASE = 0.0285  # meters

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
    steer_angle = (steer - 0.5) * 2 * MAX_STEERING_ANGLE
    dx = speed * math.sin(theta) * dt
    dy = speed * math.cos(theta) * dt
    dtheta = (speed / WHEELBASE) * math.tan(steer_angle) * dt
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
                if event.button == BUTTON_A:
                    is_autopilot = not is_autopilot
                    mode = "AUTOPILOT" if is_autopilot else "MANUEL"
                    print(f"🔄 Passage en mode {mode}")
                elif event.button == BUTTON_Y:
                    if track:
                        df = pd.DataFrame(track, columns=["x", "y", "timestamp"])

                        # === [MODIFIED] === Enhanced plot: black background, rainbow time gradient
                        plt.style.use('dark_background')
                        fig, ax = plt.subplots()

                        # Normalize time to 0-1 for color mapping
                        norm_time = (df["timestamp"] - df["timestamp"].min())
                        norm_time = norm_time / norm_time.max()

                        # Plot with a color map (rainbow)
                        scatter = ax.scatter(df["x"], df["y"], c=norm_time, cmap="rainbow", s=10)

                        ax.set_title("Trajectoire")
                        ax.set_xlabel("x")
                        ax.set_ylabel("y")
                        ax.axis("equal")
                        ax.grid(True, color='gray', linestyle='--', linewidth=0.5)

                        # Add colorbar for time reference
                        cbar = plt.colorbar(scatter, ax=ax, label="Temps (normalisé)")

                        # Ensure directory exists
                        os.makedirs("plot", exist_ok=True)
                        plt.savefig("plot/plot.png")
                        plt.close()
                        print("📸 Trajectory saved to plot/plot.png")
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
            steering = STEERING_CENTER + steer_in * STEERING_RANGE
            steering = np.clip(steering, 0.0, 1.0)

            speed = 0
            if joy.get_button(BUTTON_LB): speed = -MAX_SPEED / 2
            if joy.get_button(BUTTON_RB): speed =  MAX_SPEED / 2
            if speed == 0:
                lt = joy.get_axis(AXIS_LT)
                if lt != -1.0:
                    speed = (lt + 1)* (REVERSE_SPEED)
                else:
                    rt = joy.get_axis(AXIS_RT)
                    speed = (rt + 1)* (MAX_SPEED)

            vesc.set_servo(steering + STEERING_OFFSET)
            vesc.set_duty_cycle(speed)

            # === [MODIFIED] === Update and log coordinates in manual mode ===
            # sim_speed = np.interp(speed, [REVERSE_SPEED, MAX_SPEED], [-1, 1])
            # sim_steer = np.clip(steering, 0.0, 1.0)
            msg = vesc.get_measurements()
            print(f"get_measurements: {"none" if msg is None else msg.duty_cycle_now}")
            x, y, theta = update_position(x, y, theta, speed, steering, dt)
            track.append((x, y, now))
            print(f"[MAN] {steering=:.2f} | {speed=:.3f}", end=" ")
            print(f"📍 Pos: ({x:.2f}, {y:.2f}) | θ: {math.degrees(theta)%360:.1f}°")

        time.sleep(0.01)

except KeyboardInterrupt:
    pass

finally:
    vesc.set_duty_cycle(0)
    vesc.set_servo(0.5)
    pygame.quit()
    print("✅ Arrêt propre")

