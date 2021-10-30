#Import necessary libraries
from flask import Flask, render_template, url_for, redirect, Response
import cv2
import mediapipe as mp
import numpy as np
import os  
import time
import subprocess
import random
from datetime import datetime

# Import module for coaching
import pafy
from gtts import gTTS
from playsound import playsound

# white baton pipeline
from pipeline import YOUTUBE_SOURCE, COMMEND_SOURCE, GYRO_SOURCE, AUDIO_DIR

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
CAMERA = cv2.VideoCapture(0) # Golbal CAMERA

#Initialize the Flask app
app = Flask(__name__)

vib_states = {
    'UP':   0,
    'DOWN': 0,
    'LEFT': 0,
    'RIGHT':0,
}
vib_list = list(vib_states.keys())

# CAMERA STREAM
def gen_frames():  
    while True:
        success, frame = CAMERA.read()  # read the CAMERA frame
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
        
            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) 

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

# CAMERA STREAM: landmark
def gen_landmark_frames():  
    while True:
        success, frame = CAMERA.read()  # read the CAMERA frame
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
        
            # Make detection
            results = pose.process(image)
            try:
                landmarks = results.pose_landmarks.landmark
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

# CAMERA STREAM: surround
def gen_surround_frams():
    pass

# CAMERA_STREAM: coaching
def get_video_from_url(URL):
    """
    Creates a new video streaming object to extract video frame by frame to make prediction on.
    :return: opencv2 video capture object, with lowest quality frame available for video.
    """
    play = pafy.new(URL).streams[0]
    assert play is not None
    return cv2.VideoCapture(play.url)

def calculate_2Dangle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle >180.0: angle = 360-angle
    return angle 

def norm(v): 
    v = np.array(v)
    norm_v = np.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return norm_v

def calculate_3Dangle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0: angle = 360-angle
    return angle 

def gen_coach_frames():
    _tmp = np.zeros(2)
    player1 = get_video_from_url(YOUTUBE_SOURCE)
    player2 = CAMERA
    while True:
        ret1, frame1 = player1.read()
        ret2, frame2 = player2.read()
        #assert player1.isOpened()
        #assert player2.isOpened()
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose1:
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose2:
                _tmp[0] = time.time() # store time for optimized list printing

                ### 1. Pose Estimation of Contents ###

                start_time1 = time.time()
                #ret1, frame1 = player1.read()
                #assert ret1

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                frame1.flags.writeable = False
                image1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                
                try:
                    
                    results1 = pose1.process(image1)

                    if results1 is None:
                        continue

                    # Draw the pose annotation on the image.
                    image1.flags.writeable = True
                    image1 = cv2.cvtColor(image1, cv2.COLOR_RGB2BGR)
                    mp_drawing.draw_landmarks(image1,
                                                results1.pose_landmarks,
                                                mp_pose.POSE_CONNECTIONS
                                                )
                    # Check Performance
                    end_time1 = time.time()
                    fps1 = 1/np.round(end_time1 - start_time1, 3)
                    #print(f"Youtube _ Frames Per Second : {fps1}")


                    ### 2. Pose Estimation of User ###

                    start_time2 = time.time()
                    #ret2, frame2 = player2.read()
                    #assert ret2

                    # To improve performance, optionally mark the image as not writeable to
                    # pass by reference.
                    frame2.flags.writeable = False
                    image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                    results2 = pose2.process(image2)

                    if results2 is None:
                        continue

                    # Draw the pose annotation on the image.
                    image2.flags.writeable = True
                    image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)
                    mp_drawing.draw_landmarks(image2,
                                                results2.pose_landmarks,
                                                mp_pose.POSE_CONNECTIONS
                                                )
                    # Check Performance
                    end_time2 = time.time()
                    _tmp[1] = end_time2
                    fps2 = 1/np.round(end_time2 - start_time2, 3)
                    #print(f"USER _ Frames Per Second : {fps2}")

                    ### 3. Plot in Concatentaed Fashion
                    image1_rev = cv2.resize(image1, (400, 200))
                    image2_rev = cv2.resize(image2, (400, 200))
                    image2_rev = cv2.flip(image2_rev,1)

                    imstack = np.vstack([image1_rev,image2_rev])

                    #cv2.namedWindow("Comparison")
                    #cv2.imshow('Comparison',imstack)

                    ### 4. Logic ### 
                    if int(time.time())%10 == 0: # ~ 1 operation per about 5 frames
                        _tmp[0] = _tmp[1]; _tmp[1] = 0 # renewal time
                        landmarks1 = results1.pose_landmarks.landmark
                        landmarks2 = results2.pose_landmarks.landmark
                        ldmk1 = np.array(landmarks1)
                        ldmk2 = np.array(landmarks2)
                        for i in range(33):
                            ldmk1[i] = np.array([ldmk1[i].x, ldmk1[i].y, ldmk1[i].z, ldmk1[i].visibility])
                            ldmk2[i] = np.array([ldmk2[i].x, ldmk2[i].y, ldmk2[i].z, ldmk2[i].visibility])

                        dist = np.zeros(4) # list of distance
                        dist[0] = abs(calculate_2Dangle(ldmk1[13][0:2], ldmk1[11][0:2], ldmk1[23][0:2]) - calculate_2Dangle(ldmk2[13][0:2], ldmk2[11][0:2], ldmk2[23][0:2])) 
                        dist[1] = abs(calculate_2Dangle(ldmk1[14][0:2], ldmk1[12][0:2], ldmk1[24][0:2]) - calculate_2Dangle(ldmk2[14][0:2], ldmk2[12][0:2], ldmk2[24][0:2]))
                        dist[2] = abs(calculate_2Dangle(ldmk1[11][0:2], ldmk1[13][0:2], ldmk1[15][0:2]) - calculate_2Dangle(ldmk2[11][0:2], ldmk2[13][0:2], ldmk2[15][0:2]))
                        dist[3] = abs(calculate_2Dangle(ldmk1[12][0:2], ldmk1[14][0:2], ldmk1[16][0:2]) - calculate_2Dangle(ldmk2[12][0:2], ldmk2[14][0:2], ldmk2[16][0:2]))

                        #tmp = dist[0]
                        k = 0
                        for i in [1,2,3]:
                            if dist[i] > dist[0]:
                                dist[0] = dist[i] 
                                k = i
                        if dist[0] < 30:
                            continue 
                            
                        else:
                            subprocess.call("python play_audio_cache.py -c {0}".format(str(k)))
                            print("Process: Audio - {0}".format(str(k)))

                except ValueError as e:
                    print("********************************{0}".format(e))
                    pass
        
        if not (ret1 and ret2):
            #break
            pass
        else:
            ret, buffer = cv2.imencode('.jpg', imstack)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route("/")
def home():
    return render_template('home.html', vib_states = vib_states)

@app.route("/index")
def index():
	return render_template("index.html", vib_states = vib_states) 

@app.route('/sensor_feed')
def sensor_feed():
    def generate():
        with open(GYRO_SOURCE) as f:
            data_string = f.readlines()
        if len(data_string) == 0:
            yield "None"
        else:
            yield data_string[0] # return also will work
    return Response(generate(), mimetype='text') 

@app.route('/commend_feed')
def commend_feed():
    def generate():
        with open(COMMEND_SOURCE) as f:
            data_string = f.readlines()
        if len(data_string) == 0:
            yield "None"
        else:
            yield data_string[0] # return also will work
    return Response(generate(), mimetype='text') 

@app.route('/time_feed')
def time_feed():
    def generate():
        yield datetime.now().strftime("%Y.%m.%d|%H:%M:%S")  # return also will work
    return Response(generate(), mimetype='text') 

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/surround_guide")
def surround_guide():
	return render_template("surround_guide.html") 

@app.route('/surround_guide_video_feed')
def surround_guide_video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/real_time_coaching_with_voice")
def real_time_coaching_with_voice():
	return render_template("real_time_coaching_with_voice.html") 

@app.route('/real_time_coaching_with_voice_video_feed')
def real_time_coaching_with_voice_video_feed():
    return Response(gen_coach_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
