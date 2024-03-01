from gevent import pywsgi
from flask import Flask,jsonify
from flask_sockets import Sockets
from geventwebsocket.handler import WebSocketHandler
import cv2
import base64
import threading
import gevent
import json
import time
import os
from gevent import pywsgi
import datetime
from flask_cors import CORS

app = Flask(__name__)
sockets = Sockets(app)
CORS(app)

rtsp_url = 'rtsp://admin:Deevia@123@192.168.1.7:554/?h264x=4'

class FrameGenerator:
    def __init__(self, rtsp_url):
        self.curr_frame = None
        self.curr_frame1=None
        self.cap = cv2.VideoCapture(rtsp_url)
        self.cap1=cv2.VideoCapture(0)
        self.camera_connected=True
        if not self.cap.isOpened():
            print("Error: Couldn't open the camera.")
            self.camera_connected = False
        else:
            self.camera_connected = True

    def generate_frames(self):
        try:
            while True:
                if self.camera_connected:
                    
                    ret, frame = self.cap.read()
                    if not ret:
                        print("Error: Couldn't read frame from the camera.")
                        self.camera_connected = False
                        continue
                    self.curr_frame = frame
                
                else:
                    self.cap.release()
                    self.cap = cv2.VideoCapture(rtsp_url)
                    if self.cap.isOpened():
                        print("Camera reconnected.")
                        self.camera_connected = True
                    else:
                        time.sleep(0.01)
                time.sleep(0.01) 

        except Exception as e:
            print("Error in generating frame:", e)

    def generate_frames1(self):
        try:
            while True:
                if self.camera_connected:
                    ret,frame=self.cap1.read()

                    if not ret:
                        print("Error : Couldnt read frame from the camera")
                        self.camera_connected=False
                        continue
                    self.curr_frame1=frame
                else:
                    self.cap1.release()
                    self.cap1=cv2.VideoCapture(0)
                    if self.cap1.isOpened():
                        print("Camera Reconnected")
                        self.camera_connected=True
                    else:
                        time.sleep(0.01)
                    time.sleep(0.01)
        except Exception as e:
             print("Error in generating frame:", e)
frame_generator = FrameGenerator(rtsp_url)

@sockets.route('/video_feed')
def video_feed_socket(ws):
    while True:
        frame = frame_generator.curr_frame
        frame1=frame_generator.curr_frame1
        if frame is not None and frame1 is not None :
            outFrame = cv2.imencode('.jpg', frame)[1].tobytes()
            outframe1 = cv2.imencode('.jpg', frame1)[1].tobytes()
            image_64_encode = base64.b64encode(outFrame).decode('ascii')
            image_64_encode1 = base64.b64encode(outframe1).decode('ascii')
            result = json.dumps({'image_1': image_64_encode,'image_2': image_64_encode1})
            if not ws.closed:
                ws.send(result)
        gevent.sleep(0.01)


last_captured_images_cam1 = []
last_captured_images_cam2 = []

@app.route('/capture_frame', methods=['POST'])
def capture_frame():
    print('capture_frame')
    try:
        frame = frame_generator.curr_frame
        frame1 = frame_generator.curr_frame1
        if frame is not None and frame1 is not None:
            save_dir = r'C:\Users\DSI-LPT-006\Desktop\Data'
            today_date = datetime.datetime.now().strftime("%d-%m-%Y")
            cam1_dir = os.path.join(save_dir, 'cam1', today_date)
            cam2_dir = os.path.join(save_dir, 'cam2', today_date)
         
            os.makedirs(cam1_dir, exist_ok=True)
            os.makedirs(cam2_dir, exist_ok=True)
            current_time = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            file_name = f"cam_1_{current_time}.jpg"
            file_name1 = f"cam_2_{current_time}.jpg"
            file_path = os.path.join(cam1_dir, file_name)
            file_path1 = os.path.join(cam2_dir, file_name1)
            cv2.imwrite(file_path, frame)
            cv2.imwrite(file_path1, frame1)
            print(f"Frame captured and saved at: {file_path}")
            print(f"Frame2 captured and saved at: {file_path1}")
            
            _, buffer = cv2.imencode('.jpg', frame)
            _, buffer1 = cv2.imencode('.jpg', frame1)
            encoded_string = base64.b64encode(buffer).decode('utf-8')
            encoded_string1 = base64.b64encode(buffer1).decode('utf-8')
           
            last_captured_images_cam1.append(encoded_string)
            last_captured_images_cam2.append(encoded_string1)

            
            if len(last_captured_images_cam1) > 2:
                last_captured_images_cam1.pop(0)
            if len(last_captured_images_cam2) > 2:
                last_captured_images_cam2.pop(0)
            
            res = {
                'cam1': last_captured_images_cam1,
                'cam2': last_captured_images_cam2
            }
           
            return json.dumps(res), 200
        else:
            return "Error: No frame available to capture", 500 
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    t1 = threading.Thread(target=frame_generator.generate_frames)
    t1.start()
    t2 = threading.Thread(target=frame_generator.generate_frames1)
    t2.start()
  
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    print("Server running...")
    server.serve_forever()