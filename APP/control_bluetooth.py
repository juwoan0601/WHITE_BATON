from bluetooth import *
import argparse

BLUETOOTH_PAIR_KEY = "98:D3:71:F9:B8:8B" # WHITE-BATON-1

def send_message(msg:str):
    socket = BluetoothSocket( RFCOMM )
    try: 
        socket.connect((BLUETOOTH_PAIR_KEY, 1))
    except OSError:
        return False
    print("[{0}] Device Control Commend: {1}".format(BLUETOOTH_PAIR_KEY, msg))
    socket.send(msg)
    socket.close()

def get_message():
    socket = BluetoothSocket( RFCOMM )
    socket.connect((BLUETOOTH_PAIR_KEY, 1))
    msg = socket.recv(24)
    print("[{0}] Device Control Recieve: {1}".format(BLUETOOTH_PAIR_KEY, msg))
    socket.close()
    return msg

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--msg', type=str, help='message to send by bluetooth')
    args = parser.parse_args()
    send_message(args.msg)
