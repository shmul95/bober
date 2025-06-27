FROM arm64v8/python:3.8-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libusb-1.0-0 libusb-1.0-0-dev \
        libglib2.0-0 libgl1-mesa-glx \
	    python3-opencv python3-pip \
	     && apt-get clean \
	      && rm -rf /var/lib/apt/lists/*
	      
# Copy requirements.txt first so Docker can cache dependencies
COPY requirements.txt .

# Install dependencies (cached unless requirements.txt changes)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code (frequently changed)
COPY raycast.py .
COPY test_blob.py .
COPY unet_openvino_2022.1_6shave.blob .

CMD ["python", "test_blob.py"]
