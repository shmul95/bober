FROM nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.9-py3

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/usr/local/cuda/targets/aarch64-linux/lib:$LD_LIBRARY_PATH
WORKDIR /app

# 1) On supprime le dépôt Kitware (cause erreur GPG), 
#    puis on installe nos paquets système
RUN rm -f /etc/apt/sources.list.d/kitware* \
 && sed -i '/kitware/d' /etc/apt/sources.list \
  && apt-get update \
   && apt-get install -y \
         libusb-1.0-0 libusb-1.0-0-dev libudev1 \
	       libgl1-mesa-glx libglib2.0-0 \
	             python3-opencv python3-numpy python3-pip \
		      && rm -rf /var/lib/apt/lists/*
		      
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel \
 && pip3 install --no-cache-dir -r requirements.txt \
 && pip3 install --no-cache-dir importlib_resources

# 3) Copier scripts et modèle
COPY mask.py .
COPY raycast.py .
COPY unet_pytorch.pth .

CMD ["python3", "mask.py"]
