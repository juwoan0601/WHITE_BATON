from bluetooth import *
import argparse
import time
import os
from datetime import datetime

from pipeline import BLUETOOTH_DIR, GYRO_SOURCE

BLUETOOTH_PAIR_KEY_2 = "98:D3:71:F9:B8:8B" # WHITE-BATON-2

def connect_device(MAC_KEY):
    socket = BluetoothSocket( RFCOMM )
    
    try:
        socket.connect((MAC_KEY, 1))
        return True, socket
    except OSError as e:
        print("Connect Failed - {0}. {1}".format(MAC_KEY,e))
        return False, socket
    
def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
        except SystemError as e:
            print("Wrong Socket. {0}".format(e))
            return b"00000a00000a00000a\n"
        if not packet:
            return None
        data.extend(packet)
    return data

def data_to_float(data:str):
    dex = [10,1,0.1,0.01]
    if len(data) == 5:
        num = 0
        for d in range(4):
            num = num + dex[d]*int(data[d+1])
        if data[0] == '1': num = num*-1
        return num
    else:
        print("data length is not matched. return 0")
        return 0.0

def stream_data(socket, data_length=19, deliminator=b'\n'):
    try:
        in_char = ""
        start_char = deliminator
        while not (start_char == in_char):
            in_char = socket.recv(1)
            print(in_char)
        while True:         
            try:
                #recv_data = socket.recv(19)
                recv_data = recvall(socket,data_length)
                if len(recv_data) < data_length:
                    continue
                data_string = str(recv_data,'utf-8').replace('\n','')
                data_token = list(filter(None,data_string.split('a')))
                acc_val = [round(data_to_float(d),2) for d in data_token]
                print("[{0}] Write {1}".format(datetime.now().strftime("%Y.%m.%d|%H:%M:%S"),",".join(list(map(str,acc_val)))))
                with open(GYRO_SOURCE,'w') as f:
                    f.write(",".join(list(map(str,acc_val))))
            except KeyboardInterrupt:
                print("disconnected")
                socket.close()
                print("all done")
                return False
    except btcommon.BluetoothError as err:
        print('An error occurred : %s ' % err)
        pass

if __name__ == "__main__":
    os.makedirs(BLUETOOTH_DIR, exist_ok=True)
    with open(GYRO_SOURCE,'w') as f:
        f.write(",".join(["0","0","0","0"]))
    is_connect_recv, socket_recv = connect_device(BLUETOOTH_PAIR_KEY_2)
    if is_connect_recv: stream_data(socket_recv)
    else: print("Connection Falied")


