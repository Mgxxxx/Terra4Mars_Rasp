import serial
import time

def send_rover_command(ser, direction, wheel_speeds, servo_angle):
    if direction not in [0, 1]:
        raise ValueError("Direction must be 0 or 1.")
    if len(wheel_speeds) != 4 or any(not (0 <= s <= 127) for s in wheel_speeds):
        raise ValueError("Each wheel speed must be in 0–127.")
    if not (0 <= servo_angle <= 255):
        raise ValueError("Servo angle must be in 0–255.")

    # Send 6 bytes: Start + 5 data bytes
    data = bytearray()
    data.append(49)  # ASCII '1' start marker (as used by Arduino)
    data.append(direction)
    data.extend(wheel_speeds)
    data.append(servo_angle)

    ser.write(data)
    print(f"Sent bytes: {[hex(b) for b in data]}")

def main():
    ser = serial.Serial('/dev/pts/1', 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to reset

    try:
        while True:
            direction = int(input("Direction (0=FWD, 1=BWD): "))
            wheel_speeds = [int(input(f"Wheel {i+1} speed (0–127): ")) for i in range(4)]
            servo_angle = int(input("Servo angle (0–255): "))

            send_rover_command(ser, direction, wheel_speeds, servo_angle)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()