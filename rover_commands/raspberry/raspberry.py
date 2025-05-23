import socket
import serial

# Serial to your rover
SERIAL_PORT = "/dev/pts/2"
BAUDRATE    = 9600

# Network listener
LISTEN_IP   = "0.0.0.0"  # all interfaces
LISTEN_PORT = 9999

# Prep serial
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

# Prep UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))
print(f"Listening for packets on UDP {LISTEN_PORT}…")

try:
    while True:
        packet, addr = sock.recvfrom(64)
        # Expect exactly 1 + 4 + 1 = 6 bytes
        if len(packet) != 6 or packet[0] != 255:
            print("Bad packet from", addr, packet)
            continue

        # Forward the raw packet straight to serial:
        ser.write(packet)
        print("Forwarded to rover:", [hex(b) for b in packet])

except KeyboardInterrupt:
    print("Receiver stopping…")
finally:
    ser.close()
    sock.close()