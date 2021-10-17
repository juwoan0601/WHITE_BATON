from bluetooth import *
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--msg', type=str, help='message to send by bluetooth')
args = parser.parse_args()

BLUETOOTH_PAIR_KEY = "98:d3:11:f8:79:27" # WHITE-BATON-1

if __name__ == '__main__':
    socket = BluetoothSocket( RFCOMM )
    socket.connect((BLUETOOTH_PAIR_KEY, 1))
    print("[{0}] LED Control Commend: {1}".format(BLUETOOTH_PAIR_KEY, args.msg))
    socket.send(args.msg)
    socket.close()