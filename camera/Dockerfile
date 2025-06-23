FROM python:3.12.3-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libusb-1.0-0 libusb-1.0-0-dev libudev1 \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

RUN pip install --no-cache-dir depthai flask numpy opencv-python

COPY mjpeg_stream.py .

EXPOSE 5000

CMD ["python", "mjpeg_stream.py"]