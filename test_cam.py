from flask import Flask, Response
import depthai as dai
import cv2

# Créez le pipeline DepthAI
pipeline = dai.Pipeline()
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setFps(30)

xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

# Initialise Flask
app = Flask(__name__)

def gen_frames():
    """Génère les frames encodées en JPEG pour le streaming MJPEG"""
    # Lance le device avec le pipeline construit
    with dai.Device(pipeline) as device:
        # Queue pour récupérer les frames RGB
        q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        while True:
            # Récupère la frame
            frame = q_rgb.get().getCvFrame()
            # En cas de problème de frame
            if frame is None or frame.size == 0:
                continue
            # Encode en JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            # Retourne le bytes sous forme de chunk
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Route HTTP qui renvoie un flux MJPEG continu"""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Lance l'application Flask sur toutes les interfaces (accessible depuis le réseau local)
    app.run(host='0.0.0.0', port=5000, threaded=True)
