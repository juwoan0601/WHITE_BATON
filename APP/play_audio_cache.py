import argparse
from gtts import gTTS
from playsound import playsound
import os
import time
from pipeline import AUDIO_DIR,COMMEND_SOURCE, BLUETOOTH_DIR

def play_audio_cache(path:str):
    playsound(path)
    if os.path.isfile(path):
        os.remove(path)

def make_audio_cache(cmd:str):
    if cmd == "0":
        text = '왼팔의 위치.'
        tts = gTTS(text = text, lang = 'ko', slow = False)
        with open(COMMEND_SOURCE, 'w') as f: 
            f.writelines(["0001"])
    elif cmd == "1":
        text = '오른팔의 위치.'
        tts = gTTS(text = text, lang = 'ko', slow = False)
        with open(COMMEND_SOURCE, 'w') as f: 
            f.writelines(["0010"])
    elif cmd == "2":
        text = '왼쪽 팔꿈치.'
        tts = gTTS(text = text, lang = 'ko', slow = False)
        with open(COMMEND_SOURCE, 'w') as f: 
            f.writelines(["0100"])
    elif cmd == "3":
        text = '오른쪽 팔꿈치.'
        tts = gTTS(text = text, lang = 'ko', slow = False)
        with open(COMMEND_SOURCE, 'w') as f: 
            f.writelines(["1000"])

    audio_file_name = '{0}/guide_{1}.mp3'.format(AUDIO_DIR,str(int(time.time())))
    tts.save(audio_file_name)
    playsound(audio_file_name)
    if os.path.isfile(audio_file_name):
        os.remove(audio_file_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='File Path to Play')
    parser.add_argument('-c','--commend', type=str, help='commend for gen audio')
    args = parser.parse_args()
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(BLUETOOTH_DIR, exist_ok=True)
    make_audio_cache(args.commend)