#!/usr/bin/env bash
set -euo pipefail

IMAGE="robocar-drive:latest"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "Image $IMAGE introuvable, lancement du build…"
  docker build -t "$IMAGE" ./drive
fi

echo "Démarrage du container $IMAGE…"
docker run --privileged \
  -e SDL_VIDEODRIVER=dummy \
  --device /dev/ttyACM0:/dev/ttyACM0 \
  "$IMAGE"
