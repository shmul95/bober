
import depthai as dai
import numpy as np
import cv2
import os

IMG_W, IMG_H = 320, 192
BLOB_PATH = "unet_openvino_2022.1_6shave.blob"

# Pipeline
pipeline = dai.Pipeline()

# 1. Camera node
cam = pipeline.create(dai.node.ColorCamera)
cam.setBoardSocket(dai.CameraBoardSocket.RGB)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam.setPreviewSize(IMG_W, IMG_H)
cam.setInterleaved(False)
cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

# 2. Neural network node
nn = pipeline.create(dai.node.NeuralNetwork)
nn.setBlobPath(BLOB_PATH)
cam.preview.link(nn.input)

# 3. Outputs
xout_cam = pipeline.create(dai.node.XLinkOut)
xout_cam.setStreamName("image")
cam.preview.link(xout_cam.input)

xout_nn = pipeline.create(dai.node.XLinkOut)
xout_nn.setStreamName("nn")
nn.out.link(xout_nn.input)

# Device
with dai.Device(pipeline) as device:
    image_q = device.getOutputQueue("image", maxSize=1, blocking=False)
    nn_q = device.getOutputQueue("nn", maxSize=1, blocking=False)

    while True:
        in_frame = image_q.get().getCvFrame()
        in_nn = nn_q.get()

        # Neural network output (HxW)
        output = np.array(in_nn.getFirstLayerFp16())
        output = output.reshape((IMG_H, IMG_W))

        # Normalize and convert to 8-bit
        mask = (output > 0.5).astype(np.uint8) * 255

        # Show results
        cv2.imshow("Camera", in_frame)
        cv2.imshow("Prediction Mask", mask)

        if cv2.waitKey(1) == ord('q'):
            break
