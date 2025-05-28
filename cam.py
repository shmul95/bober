import depthai as dai
import cv2

# Create pipeline
pipeline = dai.Pipeline()

# Add only the RGB color camera node
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setFps(30)

# Output stream to host
xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("rgb")
cam_rgb.preview.link(xout.input)

# Start device with pipeline
with dai.Device(pipeline) as device:
    q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    while True:
        frame = q_rgb.get().getCvFrame()
        cv2.imshow("RGB Camera Only", frame)

        if cv2.waitKey(1) == ord('q'):
            break

