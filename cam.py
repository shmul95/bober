import depthai as dai
import cv2
import os
from datetime import datetime
from sys import argv

pipeline = dai.Pipeline()

cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(160, 120)
cam_rgb.setInterleaved(False)
cam_rgb.setFps(1)

xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("rgb")
cam_rgb.preview.link(xout.input)

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
        print("Saved: {}".format(filename))

        frame_count += 1

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

cv2.destroyAllWindows()
