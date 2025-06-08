import depthai as dai
import cv2
import os
from datetime import datetime
from sys import argv

pipeline = dai.Pipeline()

cam = pipeline.createColorCamera()
cam.setBoardSocket(dai.CameraBoardSocket.RGB)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)  # or a lower one
cam.setIspScale(2, 2)    # e.g. 1080 p → 540 p
cam.setFps(15)           # 15 fps instead of 30 fps

# cam_rgb = pipeline.create(dai.node.ColorCamera)
# cam_rgb.setPreviewSize(320, 240)
# cam_rgb.setInterleaved(False)
# cam_rgb.setFps(1)

xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("rgb")
cam.preview.link(xout.input)

os.makedirs("data", exist_ok=True)

with dai.Device(pipeline, maxUsbSpeed=dai.UsbSpeed.HIGH) as device:
    q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    frame_count = 0

    while True:
        frame = q_rgb.get().getCvFrame()
        cv2.imshow("RGB Camera Only", frame)

        if '-p' in argv or '--preserve' in argv:
            filename = datetime.now().strftime("data/frame_%Y%m%d_%H%M%S_%f.png")
        else:
            filename = datetime.now().strftime("data/frame.png")

        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")

        frame_count += 1

        # Exit condition
        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()

