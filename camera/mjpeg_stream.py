import depthai as dai
from flask import Flask, Response
import threading
import os

app = Flask(__name__)
pipeline = dai.Pipeline()
cam = pipeline.create(dai.node.ColorCamera)
cam.setBoardSocket(dai.CameraBoardSocket.RGB)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam.setFps(30)

enc = pipeline.create(dai.node.VideoEncoder)
enc.setDefaultProfilePreset(cam.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)
cam.video.link(enc.input)

xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("mjpeg")
enc.bitstream.link(xout.input)

output_folder = '/app/data'
os.makedirs(output_folder, exist_ok=True)

frame_index = 0
max_frames = 3
filenames = [os.path.join(output_folder, f'frame_{i}.jpg') for i in range(max_frames)]

last_jpeg = None

def capture_loop():
    global last_jpeg, frame_index
    with dai.Device(pipeline, maxUsbSpeed=dai.UsbSpeed.HIGH) as device:
        q = device.getOutputQueue(name="mjpeg", maxSize=1, blocking=True)
        while True:
            packet = q.get()
            data = packet.getData()
            last_jpeg = data if isinstance(data, (bytes, bytearray)) else bytes(data)
            path = filenames[frame_index]
            with open(path, 'wb') as f:
                f.write(last_jpeg)
            frame_index = (frame_index + 1) % max_frames

threading.Thread(target=capture_loop, daemon=True).start()

@app.route('/stream')
def stream():
    def generator():
        boundary = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
        while True:
            if last_jpeg is not None:
                yield boundary + last_jpeg + b"\r\n"
    return Response(generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
