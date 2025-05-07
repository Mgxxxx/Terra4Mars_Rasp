import serial
ser = serial.Serial('/dev/pts/2', 9600)

print("Listening for rover bytes...")

while True:
    if ser.in_waiting >= 6:
        data = ser.read(6)
        print("Received:", [hex(b) for b in data])