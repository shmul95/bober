import depthai as dai
import cv2
import os
import numpy as np

# 1) Pipeline
pipeline = dai.Pipeline()
cam = pipeline.createColorCamera()
cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam.setFps(1)   # one photo per run

# 2) JPEG encoder
videoEnc = pipeline.createVideoEncoder()
videoEnc.setDefaultProfilePreset(cam.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)
cam.video.link(videoEnc.input)

# 3) XLinkOut for JPEG
xout = pipeline.createXLinkOut()
xout.setStreamName("jpeg")
videoEnc.bitstream.link(xout.input)

with dai.Device(pipeline, maxUsbSpeed=dai.UsbSpeed.HIGH) as device:
    q = device.getOutputQueue(name="jpeg", maxSize=1, blocking=True)

    frame_count = 0

    while True:
        enc = q.get()
        jpg_bytes = enc.getData()
        print("JPEG byte length:", len(jpg_bytes))
        arr = np.asarray(bytearray(jpg_bytes), dtype=np.uint8)
        print("Array shape:", arr.shape, "dtype:", arr.dtype)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        path = "data/frame.jpg"
        cv2.imwrite(path, frame)
        print(f"Saved JPEG frame to {path}")

        cv2.imshow("JPEG Frame", frame)
        cv2.waitKey(0)

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


