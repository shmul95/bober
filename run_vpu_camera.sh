#!/usr/bin/env bash
set -euo pipefail

IMAGE="robocar-vpu-maskgen:latest"

echo "Démarrage du container $IMAGE…"

sudo docker run --rm --runtime nvidia \
     --gpus all --privileged \
     -v /dev/bus/usb:/dev/bus/usb \
     -v ~/robocar/camera/data:/app/data \
     -v ~/robocar/camera/cam_mask:/app/cam_mask \
     -v /usr/local/cuda-10.2/targets/aarch64-linux/lib:/usr/local/cuda/lib64 \
     -e NVIDIA_VISIBLE_DEVICES=all \
     "$IMAGE"
