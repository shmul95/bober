#!/usr/bin/env bash
set -euo pipefail

IMAGE="robocar-maskgen:latest"

echo "Démarrage du container $IMAGE…"
sudo docker run --rm --runtime nvidia --gpus all --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  -v ~/robocar/camera/data:/app/data \
  -v ~/robocar/camera/cam_mask:/app/cam_mask \
  robocar-maskgen:latest
