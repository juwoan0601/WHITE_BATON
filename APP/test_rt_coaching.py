import cv2
import mediapipe as mp
import pafy
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from time import time, sleep
from gtts import gTTS
from playsound import playsound
import os
import subprocess


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

class RealTime_Coaching_Voice:
    """
    Class implements Pose Estimation model to make inferences on a youtube video using Opencv2.
    """

    def __init__(self, url, out_file="src_landmarks.mov"):
        """
        Initializes the class with youtube url and output file.
        :param url: Has to be as youtube URL,on which prediction is made.
        :param out_file: A valid output file name.
        """
        self._URL = url
        self.out_file = out_file
        self.tmp = np.zeros(2)

    def get_video_from_url(self):
        """
        Creates a new video streaming object to extract video frame by frame to make prediction on.
        :return: opencv2 video capture object, with lowest quality frame available for video.
        """
        play = pafy.new(self._URL).streams[0]
        assert play is not None
        return cv2.VideoCapture(play.url)

    def __call__(self):
        """
        This function is called when class is executed, it runs the loop to read the video frame by frame,
        and write the output into a new file.
        :return: void
        """
        
        player1 = self.get_video_from_url()
        player2 = cv2.VideoCapture(0)
        assert player1.isOpened()
        assert player2.isOpened()
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose1:
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose2:
                self.tmp[0] = time() # store time for optimized list printing
                while True:

                    ### 1. Pose Estimation of Contents ###

                    start_time1 = time()
                    ret1, frame1 = player1.read()
                    assert ret1

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
                        end_time1 = time()
                        fps1 = 1/np.round(end_time1 - start_time1, 3)
                        print(f"Youtube _ Frames Per Second : {fps1}")


                        ### 2. Pose Estimation of User ###

                        start_time2 = time()
                        ret2, frame2 = player2.read()
                        assert ret2

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
                        end_time2 = time()
                        self.tmp[1] = end_time2
                        fps2 = 1/np.round(end_time2 - start_time2, 3)
                        print(f"USER _ Frames Per Second : {fps2}")

                        ### 3. Plot in Concatentaed Fashion
                        image1_rev = cv2.resize(image1, (400, 200))
                        image2_rev = cv2.resize(image2, (400, 200))

                        imstack = np.vstack([image1_rev,image2_rev])

                        cv2.namedWindow("Comparison")
                        cv2.imshow('Comparison',imstack)

                        ### 4. Logic ### 

                        if self.tmp[1]-self.tmp[0] > 10: # ~ 1 operation per about 5 frames
                            self.tmp[0] = self.tmp[1]; self.tmp[1] = 0 # renewal time
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

                            tmp = dist[0]
                            k = 0
                            for i in [1,2,3]:
                                if dist[i] > dist[0]:
                                    dist[0] = dist[i] 
                                    k = i
                            if dist[0] < 30:
                                continue 
                                
                            else:
                                if k == 0:
                                    text = '왼팔의 위치가 잘못되었습니다.'
                                    tts = gTTS(text = text, lang = 'ko', slow = False)
                                elif k == 1:
                                    text = '오른팔의 위치가 잘못되었습니다.'
                                    tts = gTTS(text = text, lang = 'ko', slow = False)
                                elif k == 2:
                                    text = '왼쪽 팔꿈치의 위치가 잘못되었습니다.'
                                    tts = gTTS(text = text, lang = 'ko', slow = False)
                                elif k == 3:
                                    text = '오른쪽 팔꿈치의 위치가 잘못되었습니다.'
                                    tts = gTTS(text = text, lang = 'ko', slow = False)

                                os.makedirs("./audios_cache/", exist_ok=True)
                                audio_file_name = './audios_cache/guide_{0}.mp3'.format(str(int(time())))
                                tts.save(audio_file_name)
                                subprocess.call(["python", "play_audio_cache.py", "-p", audio_file_name])

                                '''
                                audio_file_name = './audios_cache/guide_{0}.mp3'.format(str(int(time())))
                                tts.save(audio_file_name)
                                print("Audio File Write: {0}".format(audio_file_name))
                                exec("from playsound import playsound\nplaysound(audio_file_name)", globals())
                                if os.path.isfile(audio_file_name):
                                    os.remove(audio_file_name)
                                '''
                                '''
                                file = "./audios_cache/guide_{0}.mp3".format(str(int(time())))
                                tts.save(file)
                                playsound(file)
                                if os.path.isfile(file):
                                    os.remove(file)
                                '''

                    except:
                        pass
                    
                    if cv2.waitKey(5) & 0xFF == 27:
                        break

if __name__ == "__main__":
    application = RealTime_Coaching_Voice('https://www.youtube.com/watch?v=goT7St7V9Xk')
    application()