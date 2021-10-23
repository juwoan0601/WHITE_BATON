from flask import Flask, render_template, url_for, redirect   # url_for 함수, redirect 함수 추가
import os

app = Flask(__name__)

iot_states = {                           # 전체 디바이스 현황 표시용
    'LED1':0,
    'LED2':0,
    'LED3':0,
    'LED4':0,
    'SRV1':0
}

from bluetooth import *
socket = BluetoothSocket( RFCOMM )
socket.connect(("98:d3:71:f9:b8:8b", 1))
print(socket.recv(20))


@app.route('/')                       # 기본주소('/')로 들어오면
def home():
    return render_template('index_white_baton.html', bt_data = socket.recv(20))   #index.html에 전체 led현황을 함께 전달 

@app.route('/<SID>/<int:state>')                                # 개별 led를 켜고 끄는 주소
def iot_switch(SID, state):                                    # 개별 led ON, OFF 함수
    iot_states[SID] = state
    '''
    if (SID == 'LED1') and (state == 1) : os.system('sudo python3 sendLEDCommend.py --msg=1')
    if (SID == 'LED1') and (state == 0) : os.system('sudo python3 sendLEDCommend.py --msg=2')
    if (SID == 'LED2') and (state == 1) : os.system('sudo python3 sendLEDCommend.py --msg=3')
    if (SID == 'LED2') and (state == 0) : os.system('sudo python3 sendLEDCommend.py --msg=4')
    if (SID == 'LED3') and (state == 1) : os.system('sudo python3 sendLEDCommend.py --msg=5')
    if (SID == 'LED3') and (state == 0) : os.system('sudo python3 sendLEDCommend.py --msg=6')
    if (SID == 'LED4') and (state == 1) : os.system('sudo python3 sendLEDCommend.py --msg=7')
    if (SID == 'LED4') and (state == 0) : os.system('sudo python3 sendLEDCommend.py --msg=8')
    if (SID == 'SRV1') and (state == 1) : os.system('sudo python3 sendServoCommend.py --msg=1')
    if (SID == 'SRV1') and (state == 0) : os.system('sudo python3 sendServoCommend.py --msg=2')
    '''
    #leds.value=tuple(led_states.values())
    return redirect(url_for('home'))                           # leds의 색상변경이 완료되면 redirect함수를 통해 기본주소('/')으로 이동

@app.route('/all/<int:state>')                                 # 모든 led를 한꺼번에 켜거나 끄는 주소
def all_on_off(state):                                        # 모든 led를 한꺼번에 켜거나 끄는 함수
    if state == 0:
        iot_states['LED1']=0
        iot_states['LED2']=0
        iot_states['LED3']=0 
        iot_states['LED4']=0 
        #os.system('sudo python3 sendLEDCommend.py --msg=2468') 
    elif state == 1: 
        iot_states['LED1']=1
        iot_states['LED2']=1
        iot_states['LED3']=1 
        iot_states['LED4']=1
        #os.system('sudo python3 sendLEDCommend.py --msg=1357') 
    #leds.value=tuple(led_states.values())
    return redirect(url_for('home'))                     # 모든 led를 켜거나 껐으면 기본주소('/')로 이동

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')