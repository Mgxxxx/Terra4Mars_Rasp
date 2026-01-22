"""
Raspberry Pi UDP receiver and serial forwarder.
Receives command packets from the host and relays them to the Arduino via serial.
"""

import sys
import socket
import serial

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 9999
PACKET_SIZE = 6
START_MARKER = 0xFF


def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    except serial.SerialException as e:
        print(f"Serial connection failed: {e}", file=sys.stderr)
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    print(f"Listening on UDP port {LISTEN_PORT}")

    try:
        while True:
            packet, addr = sock.recvfrom(64)

            if len(packet) != PACKET_SIZE or packet[0] != START_MARKER:
                continue

            ser.write(packet)
    except KeyboardInterrupt:
        print("\nReceiver stopped.")
    finally:
        ser.close()
        sock.close()


if __name__ == "__main__":
    main()
