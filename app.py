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
from flask_cors import CORS
app = Flask(__name__)
sockets = Sockets(app)
CORS(app)


rtsp_url = r'C:\Users\DSI-LPT-006\Downloads\hello.mp4'

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
            print("Error in generate frame:", e)

frame_generator = FrameGenerator(rtsp_url)

@sockets.route('/video_feed')
def video_feed_socket(ws):
    
    while True:
        print("Running")  
        frame = frame_generator.curr_frame
        if frame is not None:
            outFrame = cv2.imencode('.jpg', frame)[1].tobytes()
            image_64_incode = base64.b64encode(outFrame).decode('ascii')
            result =json.dumps({'image_1':image_64_incode})
            if ws.closed == False:
                ws.send(result)
            time.sleep(0.01)


# @app.route('/capture_frame', methods=['POST'])
# def capture_frame():
#     _, frame = frame_generator.cap.read()
#     _, buffers = cv2.imencode('.jpg', frame)
#     image_64_encode = base64.b64encode(buffers).decode('ascii')
#     return image_64_encode, 200

def server():
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    print("Server running...")
    server.serve_forever()

if __name__ == '__main__':
    t1 = threading.Thread(target=frame_generator.generate_frames)
    t1.start()
    t2 = threading.Thread(target=server)
    t2.start()
