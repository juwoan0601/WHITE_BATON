from bluetooth import *
import argparse
import time
import os

BLUETOOTH_PAIR_KEY_2 = "98:D3:71:F9:B8:8B" # WHITE-BATON-2
BLUETOOTH_PAIR_KEY_3 = "98:DA:60:01:72:74" # WHITE-BATON-2

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
        packet = sock.recv(n - len(data))
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
                data_string = str(recv_data,'utf-8').replace('\n','')
                data_token = list(filter(None,data_string.split('a')))
                acc_val = [round(data_to_float(d),2) for d in data_token]
                print(acc_val)
                with open("./stream_data.csv",'w') as f:
                    f.write(",".join(list(map(str,acc_val))))
            except KeyboardInterrupt:
                print("disconnected")
                socket.close()
                print("all done")
    except btcommon.BluetoothError as err:
        print('An error occurred : %s ' % err)
        pass

def stream_data_commend(socket):
    try:
        while True:         
            try:
                msg=str(time.time())
                print(socket.send(msg[-4:]))
            except KeyboardInterrupt:
                print("disconnected")
                socket.close()
                print("all done")
                return True
    except btcommon.BluetoothError as err:
        print('An error occurred : %s ' % err)
        pass

def stream_data_dual(socket_send, socket_recv):
    try:
        in_char = ""
        start_char = 'b\n'
        while not (start_char == in_char):
            in_char = socket_send.recv(1)
            print(in_char)
        while True:         
            try:
                #recv_data = socket.recv(19)
                recv_data = recvall(socket_recv,19)
                data_string = str(recv_data,'utf-8').replace('\n','')
                data_token = list(filter(None,data_string.split('a')))
                acc_val = [round(data_to_float(d),2) for d in data_token]
                print(acc_val)
                if acc_val[2] < 0.7:
                    msg="1111"
                else: 
                    msg="0000"
                socket_send.send(msg)
            except KeyboardInterrupt:
                print("disconnected")
                socket_send.close()
                socket_recv.close()
                print("all done")
    except btcommon.BluetoothError as err:
        print('An error occurred : %s ' % err)
        pass

if __name__ == "__main__":
    is_connect_recv, socket_recv = connect_device(BLUETOOTH_PAIR_KEY_2)
    #is_connect_send, socket_send = connect_device(BLUETOOTH_PAIR_KEY_3)
    if is_connect_recv: stream_data(socket_recv)
    #if is_connect_send: stream_data_commend(socket_send)
    else: print("Connection Falied")


