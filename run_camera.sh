#!/usr/bin/env bash
set -euo pipefail

IMAGE="robocar-camera:latest"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "Image $IMAGE introuvable, lancement du build…"
  docker build -t "$IMAGE" ./camera
fi

echo "Démarrage du container $IMAGE…"
docker run --rm --privileged \
  -p 5000:5000 \
  -v /dev/bus/usb:/dev/bus/usb \
  -v ~/robocar/camera/data:/app/data \
  robocar-camera:latest
