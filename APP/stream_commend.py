from bluetooth import *
import argparse
import time
from datetime import datetime

from pipeline import BLUETOOTH_DIR, COMMEND_SOURCE

BLUETOOTH_PAIR_KEY_3 = "98:DA:60:01:72:74" # WHITE-BATON-2

def connect_device(MAC_KEY):
    socket = BluetoothSocket( RFCOMM )
    try:
        socket.connect((MAC_KEY, 1))
        return True, socket
    except OSError as e:
        print("Connect Failed - {0}. {1}".format(MAC_KEY,e))
        return False, socket

def stream_data_commend(socket):
    try:
        while True:         
            try:
                with open(COMMEND_SOURCE,'r') as f:
                    msg=f.readlines()
                if len(msg) == 0:
                    continue
                else: 
                    print("[{0}] Send: {1}".format(
                        datetime.now().strftime("%Y.%m.%d|%H:%M:%S"),
                        msg[0]))
                    socket.send("{0}\n".format(msg[0]))
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print("disconnected")
                socket.close()
                print("all done")
                return True
    except btcommon.BluetoothError as err:
        print('An error occurred : %s ' % err)
        pass

if __name__ == "__main__":
    os.makedirs(BLUETOOTH_DIR, exist_ok=True)
    with open(COMMEND_SOURCE,'w') as f:
        f.writelines(["0000"])
    is_connect_send, socket_send = connect_device(BLUETOOTH_PAIR_KEY_3)
    if is_connect_send: stream_data_commend(socket_send)
    else: print("Connection Falied")


