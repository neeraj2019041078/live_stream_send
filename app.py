from gevent import pywsgi, monkey
monkey.patch_all()
from flask import Flask
from flask_sockets import Sockets
from geventwebsocket.handler import WebSocketHandler
import cv2
import base64
import threading 
import numpy as np
import json
import time
import os
from flask_cors import CORS
app = Flask(__name__)
sockets = Sockets(app)
CORS(app)



rtsp_url = r'C:\Users\DSI-LPT-006\Desktop\Slab\video.mp4'

class FrameGenerator:
    def __init__(self, rtsp_url):
        self.curr_frame = None
        self.cap = cv2.VideoCapture(rtsp_url)
        if not self.cap.isOpened():
            print("Error: Couldn't open the camera.")

    def generate_frames(self):
        try:
            while True: 
                ret, frame = self.cap.read()
                if not ret:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                
                self.curr_frame = frame
                time.sleep(0.01)
        except Exception as e:
            print("Error in generating frame:", e)

frame_generator = FrameGenerator(rtsp_url)

@sockets.route('/video_feed')
def video_feed_socket(ws):
    while True:
        frame = frame_generator.curr_frame
        if frame is not None:
            outFrame = cv2.imencode('.jpg', frame)[1].tobytes()
            image_64_encode = base64.b64encode(outFrame).decode('ascii')
            result = json.dumps({'image_1': image_64_encode})
            if not ws.closed:
                ws.send(result)
            time.sleep(0.01)

@app.route('/capture_frame', methods=['POST'])
def capture_frame():
    try: 
        _, frame = frame_generator.cap.read()
        _, buffers = cv2.imencode('.jpg', frame)
        image_64_encode = base64.b64encode(buffers).decode('ascii')
        
        image_data = base64.b64decode(image_64_encode)
        save_path = r'C:\Users\DSI-LPT-006\Desktop\Capture Images'
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, f"captured_frame_{int(time.time())}.jpg")
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        return image_64_encode, 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    t1 = threading.Thread(target=frame_generator.generate_frames)
    t1.start()
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    print("Server running...")
    server.serve_forever()
