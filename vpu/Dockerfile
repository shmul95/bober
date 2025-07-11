# Dockerfile.official
FROM luxonis/depthai-library:multiarch

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Installer usbutils pour lsusb
RUN apt-get update && apt-get install -y --no-install-recommends \
      usbutils \
    && rm -rf /var/lib/apt/lists/*

# Copier votre script et le modèle
COPY test_blob.py .
COPY unet_openvino_2022.1_6shave.blob .

# Lancer directement le script
CMD ["python3", "test_blob.py"]