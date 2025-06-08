import depthai as dai
import cv2
import os
from datetime import datetime
from sys import argv

# 1) Build pipeline
pipeline = dai.Pipeline()

cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
# halve the preview size to 320×240 to save bandwidth
cam_rgb.setPreviewSize(320, 240)
cam_rgb.setInterleaved(False)
# drop to 15 fps
cam_rgb.setFps(15)

xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("rgb")
cam_rgb.preview.link(xout.input)

# 2) Prep storage
os.makedirs("data", exist_ok=True)

# 3) Open device in USB2 mode
with dai.Device(pipeline, maxUsbSpeed=dai.UsbSpeed.HIGH) as device:
    q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    while True:
        in_rgb = q_rgb.get()  # blocking until a new frame arrives
        frame = in_rgb.getCvFrame()

        cv2.imshow("RGB Camera (USB2)", frame)

        # choose filename
        if '-p' in argv or '--preserve' in argv:
            filename = datetime.now().strftime("data/frame_%Y%m%d_%H%M%S_%f.png")
        else:
            filename = "data/frame.png"

        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()

