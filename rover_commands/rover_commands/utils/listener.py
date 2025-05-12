import serial
ser = serial.Serial('/dev/pts/2', 9600)

print("Listening for rover bytes...")

while True:
    if ser.in_waiting >= 7:
        data = ser.read(7)
        print("Received:", [hex(b) for b in data])