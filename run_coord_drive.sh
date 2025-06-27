#!/usr/bin/env bash
set -euo pipefail

IMAGE="robocar-coord-drive:latest"
HOST_CAM_DIR="$HOME/robocar/camera"
CONTAINER_APP_DIR="/app"

echo "Démarrage du container $IMAGE…"
docker run --privileged \
  -e SDL_VIDEODRIVER=dummy \
  --device /dev/ttyACM0:/dev/ttyACM0 \
  -v "$HOST_CAM_DIR":"$CONTAINER_APP_DIR/camera":ro \
  -v ~/robocar/coord-drive/plot:/app/plot \
  "$IMAGE"
