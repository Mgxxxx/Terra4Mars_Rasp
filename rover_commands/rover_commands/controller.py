"""
Standalone PS4 controller interface for direct serial communication with the rover.
Reads joystick input and transmits motor commands over serial.
"""

import os
import sys
import time
import threading

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
import serial

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
START_MARKER = 0xFF
DEADZONE = 0.1
TURN_SCALE = 0.5
POLL_RATE_HZ = 50
COMMAND_RATE_HZ = 10


def map_range(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def build_command_packet(wheel_speeds, servo_angle):
    """
    Packet format: [START_MARKER, L1, R1, L2, R2, SERVO]
    Each wheel byte encodes direction in bit 7 (0=fwd, 1=bwd) and speed in bits 0-6.
    """
    packet = bytearray([START_MARKER])
    packet.extend(wheel_speeds)
    packet.append(servo_angle)
    return packet


def joystick_poll_loop(state, lock):
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller detected. Connect a PS4 controller and restart.", file=sys.stderr)
        return

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"Controller: {js.get_name()}")

    poll_interval = 1.0 / POLL_RATE_HZ

    try:
        while True:
            pygame.event.pump()
            raw_x = js.get_axis(0)
            raw_y = js.get_axis(1)

            x = 0.0 if abs(raw_x) < DEADZONE else clamp(raw_x, -1.0, 1.0)
            y = 0.0 if abs(raw_y) < DEADZONE else clamp(-raw_y, -1.0, 1.0)

            with lock:
                state["x"] = x
                state["y"] = y

            time.sleep(poll_interval)
    except KeyboardInterrupt:
        pass
    finally:
        js.quit()
        pygame.quit()


def compute_wheel_speeds(x, y):
    """
    Compute differential wheel speeds from joystick input.
    Returns list of 4 bytes: [left_front, right_front, left_rear, right_rear]
    """
    direction = 0 if y >= 0 else 1
    base_speed = map_range(abs(y), 0, 1, 0, 127)

    left_factor = clamp(1.0 - TURN_SCALE * x, 0.0, 1.5)
    right_factor = clamp(1.0 + TURN_SCALE * x, 0.0, 1.5)

    left_speed = clamp(int(base_speed * left_factor), 0, 127)
    right_speed = clamp(int(base_speed * right_factor), 0, 127)

    # Encode direction in high bit
    left_byte = left_speed + direction * 128
    right_byte = right_speed + direction * 128

    return [left_byte, right_byte, left_byte, right_byte]


def main():
    state = {"x": 0.0, "y": 0.0}
    lock = threading.Lock()

    poll_thread = threading.Thread(target=joystick_poll_loop, args=(state, lock), daemon=True)
    poll_thread.start()

    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    except serial.SerialException as e:
        print(f"Serial connection failed: {e}", file=sys.stderr)
        sys.exit(1)

    time.sleep(2)  # Arduino reset delay
    command_interval = 1.0 / COMMAND_RATE_HZ

    try:
        while True:
            with lock:
                x, y = state["x"], state["y"]

            wheel_speeds = compute_wheel_speeds(x, y)
            servo_angle = map_range(x, -1, 1, 0, 255)
            packet = build_command_packet(wheel_speeds, servo_angle)

            ser.write(packet)
            time.sleep(command_interval)
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
