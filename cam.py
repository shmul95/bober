import depthai as dai
import cv2
import os
import numpy as np
# from datetime import datetime
# from sys import argv

pipeline = dai.Pipeline()

cam = pipeline.createColorCamera()
cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)  # or a lower one
cam.setIspScale(2, 2)    # e.g. 1080 p → 540 p
cam.setFps(1)           # 15 fps instead of 30 fps
cam.setInterleaved(True)

# cam_rgb = pipeline.create(dai.node.ColorCamera)
# cam_rgb.setPreviewSize(320, 240)
# cam_rgb.setInterleaved(False)
# cam_rgb.setFps(1)

xout = pipeline.create(dai.node.XLinkOut)
# xout.setStreamName("rgb")
xout.setStreamName("nv12")
cam.preview.link(xout.input)

os.makedirs("data", exist_ok=True)

with dai.Device(pipeline, maxUsbSpeed=dai.UsbSpeed.HIGH) as device:
    q = device.getOutputQueue(name="nv12", maxSize=1, blocking=False)

    frame_count = 0

    while True:
        try:
            # getData() returns a bytes buffer of NV12 (YUV) data
            nv12_bytes = q.get().getData()
            # compute width/height from the frame shape
            w = cam.getResolutionSize().width  // 2   # ispScale(2,2) halves it
            h = cam.getResolutionSize().height // 2
            # reshape into (h * 3/2, w) for NV12
            yuv = np.frombuffer(nv12_bytes, dtype=np.uint8).reshape((h * 3 // 2, w))
            # convert to BGR
            frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
            path = "data/frame_bgr.png"
            cv2.imwrite(path, frame)
            print(f"Saved color frame to {path}")
            cv2.imshow("Color Frame", frame)
            cv2.waitKey(0)

        except: print("an Error Occured")
        finally: cv2.destroyAllWindows()

        # frame = q.get().getCvFrame()
        # cv2.imshow("RGB Camera Only", frame)
        #
        # if '-p' in argv or '--preserve' in argv:
        #     filename = datetime.now().strftime("data/frame_%Y%m%d_%H%M%S_%f.png")
        # else:
        #     filename = datetime.now().strftime("data/frame.png")
        #
        # cv2.imwrite(filename, frame)
        # print(f"Saved: {filename}")
        #
        # frame_count += 1
        # if cv2.waitKey(1) == ord('q'): break


