# Bober — Autonomous Racing Car (Epitech project)

Summary
-------
Bober is an Epitech group project whose goal is to build small autonomous cars that can drive themselves and race between campus tracks. The project is split into three main subdomains:

- IA (AI): train and run an agent (neural network/autopilot) that controls the car to drive autonomously and perform well in races.
- WebApp: centralize telemetry, video streams and maps in a web application so teams and spectators can monitor cars in real time.
- Sensors: scripts, hardware setup and glue code for the car's sensors (camera, IMU, ultrasonic/LiDAR or other) and peripherals.

Repository structure
--------------------
This workspace contains multiple components (each has its own folder and optional Dockerfile/requirements):

- `coord-drive/` — coordination and autopilot utilities for driving logic and centralized control.
  - `autopilot.py`, `car.py`, `action_config.json`, `build.sh`, `Dockerfile`, `requirements.txt`
- `drive/` — an alternative or supporting driving stack and autopilot.
- `raycast/` — utilities for raycasting / perception (masking, raycast logic).
- `camera/` — camera capture / streaming utilities and dependencies.
- Top-level scripts: `run_drive.sh`, `run_raycast.sh`, `rebuild_coord_drive.sh` — helpers to run or rebuild components.

Goals and design
----------------
IA
--
- Train a model (supervised, reinforcement learning or imitation learning) to control throttle/steer/brake using sensor input (camera frames, optional lidar/sonar/IMU).
- Provide a training pipeline and an inference/autopilot runtime for running the model on the car.
- Evaluate performance in closed-loop simulations and real runs; log telemetry.

WebApp
------
- Provide a central web interface to:
  - View live camera feeds from each car.
  - Display car positions on a map (GPS/odometry).
  - Show telemetry (speed, heading, battery, lap times).
  - Manage races and visualize leaderboards.
- The WebApp should be accessible from a browser and support multiple simultaneous car streams.

Sensors
-------
- Provide scripts and wiring diagrams (notes) for attaching sensors to the car's compute board.
- Capture and preprocess sensor data for the IA and the WebApp.
- Offer modular drivers for different sensor types (camera, IMU, ultrasonic, LiDAR).

Getting started
---------------
Prerequisites
- Linux (development), Python 3.8+ recommended.
- Docker (optional, used by some components' Dockerfiles).
- Python dependencies are listed in each component's `requirements.txt`.

Quick run (development)
1. From the project root (`bober/`), pick a component, for example `coord-drive`:

```bash
# create a venv and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r coord-drive/requirements.txt

# run the autopilot (example)
python coord-drive/autopilot.py
```

2. To stream camera from `camera/`:

```bash
cd camera
pip install -r requirements.txt
python CAM_LIVE.py
```

3. Run raycast/perception utilities:

```bash
python raycast/raycast.py
```

Docker
------
Some components include a `Dockerfile`. You can build and run those containers for isolated environments:

```bash
cd coord-drive
./build.sh     # or: docker build -t bober-coord-drive .
./autopilot.py # or run in container per Dockerfile instructions
```

Project conventions
-------------------
- Each component aims to be runnable independently for development and testing.
- Configuration files (e.g. `action_config.json`) hold actions mappings and tuning parameters.
- Per-component `requirements.txt` keep dependencies scoped to the module.

Development notes
-----------------
- Tests: add unit tests and small integration tests for perception and autopilot logic.
- CI: add linting and type checking for Python code.
- Security: avoid shipping secrets in the repo. Use env vars for keys and credentials.

Suggested next steps
--------------------
- Flesh out the IA training README with dataset format, training scripts, and evaluation metrics.
- Add a lightweight WebApp README describing stack (React/Flask/Node), API, and how to connect car telemetry.
- Add `docs/` with wiring diagrams and sensor setup guides.

Contributors
------------
This is an Epitech student project. When contributing, follow the repository's branching and PR rules.

License
-------
Add an appropriate open-source license if you plan to share the project publicly.

Contact
-------
For questions about the project structure or to contribute, contact the project owner or open an issue in this repository.
