FROM nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.9-py3

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/usr/local/cuda/targets/aarch64-linux/lib:$LD_LIBRARY_PATH
WORKDIR /app

# 1) Clean up and install system packages
RUN rm -f /etc/apt/sources.list.d/kitware* \
 && sed -i '/kitware/d' /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y \
        libusb-1.0-0 libusb-1.0-0-dev libudev1 \
        libgl1-mesa-glx libglib2.0-0 \
        python3-opencv python3-numpy python3-pip \
 && rm -rf /var/lib/apt/lists/*

# 2) Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel \
 && pip3 install --no-cache-dir -r requirements.txt

# 3) Copy application files
COPY raycast.py .
COPY test_blob_on_oakd.py .
COPY unet_openvino_2022.1_6shave.blob .

# 4) Run the new DepthAI-based script
CMD ["python3", "test_blob_on_oakd.py"]
