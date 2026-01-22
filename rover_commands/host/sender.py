"""
Host-side UDP sender for wireless rover control.
Reads PS4 controller input and transmits command packets to the Raspberry Pi.
"""

import os
import sys
import time
import socket

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

PI_IP = "172.20.10.2"
PI_PORT = 9999
START_MARKER = 0xFF
DEADZONE = 0.05
TURN_SCALE = 0.6
SEND_RATE_HZ = 20


def map_range(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def compute_wheel_speeds(x, y):
    direction = 0 if y >= 0 else 1
    base_speed = map_range(abs(y), 0, 1, 0, 127)

    left_factor = clamp(1.0 - TURN_SCALE * x, 0.0, 1.5)
    right_factor = clamp(1.0 + TURN_SCALE * x, 0.0, 1.5)

    left_speed = clamp(int(base_speed * left_factor), 0, 127)
    right_speed = clamp(int(base_speed * right_factor), 0, 127)

    left_byte = left_speed + direction * 128
    right_byte = right_speed + direction * 128

    return [left_byte, right_byte, left_byte, right_byte]


def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller detected.", file=sys.stderr)
        sys.exit(1)

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"Controller: {js.get_name()}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_interval = 1.0 / SEND_RATE_HZ

    try:
        while True:
            pygame.event.pump()
            raw_x = js.get_axis(0)
            raw_y = -js.get_axis(1)

            x = 0.0 if abs(raw_x) < DEADZONE else raw_x
            y = 0.0 if abs(raw_y) < DEADZONE else raw_y

            wheel_speeds = compute_wheel_speeds(x, y)
            servo_angle = map_range(x, -1, 1, 0, 255)

            packet = bytearray([START_MARKER])
            packet.extend(wheel_speeds)
            packet.append(servo_angle)

            sock.sendto(packet, (PI_IP, PI_PORT))
            time.sleep(send_interval)
    except KeyboardInterrupt:
        print("\nSender stopped.")
    finally:
        js.quit()
        pygame.quit()
        sock.close()


if __name__ == "__main__":
    main()
