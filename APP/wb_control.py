from bluetooth import *

class WHITE_BATON_DEVICE:
    def __init__(self, key:str) -> None:
        self.BLUETOOTH_PAIR_KEY = key
        self.socket = BluetoothSocket( RFCOMM )

    def connect(self):
        self.socket.connect((self.BLUETOOTH_PAIR_KEY, 1))

    def disconnect(self):
        self.socket.close()

    def read(self):
        return self.socket.recv(20)


WHITE_BATON_2 = WHITE_BATON_DEVICE("98:d3:71:f9:b8:8b")

