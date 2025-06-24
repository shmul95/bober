#!/usr/bin/env bash
set -euo pipefail

IMAGE="robocar-drive:latest"

echo "Démarrage du container $IMAGE…"
docker run --privileged \
  -e SDL_VIDEODRIVER=dummy \
  --device /dev/ttyACM0:/dev/ttyACM0 \
  "$IMAGE"
