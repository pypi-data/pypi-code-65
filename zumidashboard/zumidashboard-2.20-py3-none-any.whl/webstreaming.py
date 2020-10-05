from zumi.util.camera import Camera
from flask import Flask, render_template, Response
import threading
import os
import cv2
import argparse
import subprocess

class StreamingGenerator:
    def __init__(self, camera):
        self.outputFrame = None
        self.lock = threading.Lock()
        self.camera = camera
        self.camera.start_camera()


    def capturing(self):
        if not os.path.isdir('/home/pi/Dashboard/DriveImg'):
            os.makedirs('/home/pi/Dashboard/DriveImg')

        while True:
            frame = self.camera.capture()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite('/home/pi/Dashboard/DriveImg/drivescreen.jpg', frame)

            with self.lock:
                self.outputFrame = frame.copy()


    def generate(self):
        while True:
            with self.lock:
                if self.outputFrame is None:
                    continue

                (flag, encodedImage) = cv2.imencode(".jpg", self.outputFrame)

                if not flag:
                    continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


app = Flask(__name__)
app.camera = Camera(320, 240)
app.streamingGenerator = StreamingGenerator(app.camera)
t = threading.Thread(target=app.streamingGenerator.capturing)
t.daemon = True
t.start()


@app.route('/')
def index():
   return render_template('drivescreen.html')


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/video_feed')
def video_feed():
   return Response(app.streamingGenerator.generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--protocol", type=str, required=True, help="https or http")
    args = vars(ap.parse_args())

    if args["protocol"] == "https":
        app.run(host='0.0.0.0', debug=True, threaded=True, port=3456, use_reloader=False, ssl_context=(
        "/usr/local/lib/python3.5/dist-packages/zumidashboard/crt/zumidashboard_ai.crt",
        "/usr/local/lib/python3.5/dist-packages/zumidashboard/crt/private.key"))
    else:
        app.run(host='0.0.0.0', debug=True, threaded=True, port=3456, use_reloader=False)