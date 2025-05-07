import serial
import time
import pygame
from rover_commands.rover_commands.utils.utils import update_position

# Utility to map joystick input to value range
def map_range(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def send_rover_command(ser, direction, wheel_speeds, servo_angle):
    data = bytearray()
    data.append(49)  # Start marker: ASCII '1'
    data.append(direction)
    data.extend(wheel_speeds)
    data.append(servo_angle)
    ser.write(data)
    print(f"Sent: {[hex(b) for b in data]}")

def main():
    # Initialize joystick
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("No joystick detected.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    # Initialize serial
    ser = serial.Serial('/dev/pts/1', 9600, timeout=1)
    time.sleep(2)

    try:
        while True:
            pygame.event.pump()

            x = joystick.get_axis(0)  # Left-right
            y = -joystick.get_axis(1)  # Forward-backward (invert Y)

            # Direction: 0 = forward, 1 = backward
            direction = 0 if y >= 0 else 1

            # Speed: scale |y| from 0-1 to 0-127
            speed = map_range(abs(y), 0, 1, 0, 127)
            wheel_speeds = [speed] * 4  # Uniform speed

            # Servo: scale x (-1 to 1) to 0–255
            servo_angle = map_range(x, -1, 1, 0, 255)

            send_rover_command(ser, direction, wheel_speeds, servo_angle)
            update_position(wheel_speeds, servo_angle)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        joystick.quit()
        pygame.quit()
        ser.close()

if __name__ == "__main__":
    main()