import serial
import time
import threading
import pygame

# Utility to map joystick input to value range
def map_range(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def send_rover_command(ser, wheel_speeds, servo_angle):
    data = bytearray()
    data.append(255)  # Start marker
    data.extend(wheel_speeds)
    data.append(servo_angle)
    ser.write(data)
    print(f"Sent: {[hex(b) for b in data]}")

def joystick_thread_fn(state, lock, deadzone=0.1, poll_rate=0.02):
    """Continuously polls the first PS4 controller and updates state['x'], state['y']."""
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick detected! Plug in your PS4 controller and restart.")
        return

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"Joystick detected: {js.get_name()}")

    try:
        while True:
            pygame.event.pump()  # must be called to update internal state

            # PS4 Left-stick: axis 0 = left/right, axis 1 = up/down
            raw_x = js.get_axis(0)
            raw_y = js.get_axis(1)

            # apply deadzone
            x_new = 0.0 if abs(raw_x) < deadzone else raw_x
            y_new = 0.0 if abs(raw_y) < deadzone else raw_y

            # clamp & invert Y if you want "up" to be positive
            y_new = -y_new
            x_new = max(-1.0, min(1.0, x_new))
            y_new = max(-1.0, min(1.0, y_new))

            with lock:
                state['x'] = x_new
                state['y'] = y_new

            time.sleep(poll_rate)
    except KeyboardInterrupt:
        pass
    finally:
        js.quit()
        pygame.quit()

def main():
    # Shared state
    state = {'x': 0.0, 'y': 0.0}
    lock = threading.Lock()

    # Start the joystick‐polling thread
    t = threading.Thread(target=joystick_thread_fn, args=(state, lock), daemon=True)
    t.start()

    # Initialize serial
    ser = serial.Serial('/dev/pts/1', 9600, timeout=1)
    time.sleep(2)

    try:
        while True:
            # Grab the latest inputs
            with lock:
                x, y = state['x'], state['y']

            direction = 0 if y >= 0 else 1
            speed = map_range(abs(y), 0, 1, 0, 127)

            # Turning logic
            turn_scale = 0.5
            left_factor = max(0.0, min(1.5, 1.0 - turn_scale * x))
            right_factor = max(0.0, min(1.5, 1.0 + turn_scale * x))

            left_speed  = max(0, min(127, int(speed * left_factor)))
            right_speed = max(0, min(127, int(speed * right_factor)))
            # pack direction into speeds if that’s still needed
            wheel_speeds = [
                left_speed  + direction * 127,
                right_speed + direction * 127,
                left_speed  + direction * 127,
                right_speed + direction * 127,
            ]

            servo_angle = map_range(x, -1, 1, 0, 255)

            send_rover_command(ser, wheel_speeds, servo_angle)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting…")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
