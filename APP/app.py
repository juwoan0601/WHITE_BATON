#Import necessary libraries
from flask import Flask, render_template, url_for, redirect, Response
import cv2
import mediapipe as mp
import numpy as np
import os  
import time
import subprocess
from control_bluetooth import get_message, send_message
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

#Initialize the Flask app
app = Flask(__name__)

vib_states = {
    'UP':   0,
    'DOWN': 0,
    'LEFT': 0,
    'RIGHT':0,
}
vib_list = list(vib_states.keys())

camera = cv2.VideoCapture(0)
def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
        
            # Make detection
            results = pose.process(image)
            try:
                landmarks = results.pose_landmarks.landmark
                print(landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].visibility)
                if landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].visibility > 0.9:
                    subprocess.Popen(["python", "control_bluetooth.py", "--msg=1111"])
                else: 
                    subprocess.Popen(["python", "control_bluetooth.py", "--msg=0000"])
            except AttributeError:
                pass
        
            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                    )  

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def gen_sensors():
    while True: yield str(np.random.rand())

@app.route("/")
def home():
    return render_template('home.html', vib_states = vib_states)

@app.route("/index")
def index():
	return render_template("index.html", vib_states = vib_states) 

@app.route('/<SID>/<int:state>')
def device_switch(SID, state):                                    
    vib_states[SID] = state
    #os.system('python sendBluetoothCommend.py --msg={0}'.format(''.join([str(vib_states[v]) for v in vib_list])))
    subprocess.call(["python", "control_bluetooth.py", "--msg={0}".format(''.join([str(vib_states[v]) for v in vib_list]))])
    return redirect(url_for('index')) 

@app.route('/sensor_feed')
def sensor_feed():
    return Response(gen_sensors(), mimetype='text')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
