import serial

def main():
    port = serial.serial("/dev/ttyAMA0")
    port.baudrate = 9600
