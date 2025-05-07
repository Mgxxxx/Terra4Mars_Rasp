import serial
import time
import threading

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

def input_thread_fn(state, lock):
    """
    Runs in its own thread, blocks on input() only when you type new values.
    """
    while True:
        try:
            raw = input("New joystick x,y or Ctrl-C to quit: ")
        except EOFError:
            break
        parts = raw.strip().split()
        if len(parts) != 2:
            print("Please enter exactly two numbers.")
            continue
        try:
            x_new = float(parts[0])
            y_new = float(parts[1])
        except ValueError:
            print("Couldn't parse floats. Try again.")
            continue

        # Clamp
        x_new = max(-1.0, min(1.0, x_new))
        y_new = max(-1.0, min(1.0, y_new))

        with lock:
            state['x'] = x_new
            state['y'] = y_new
            # You could also set a flag here if you want to detect “just changed”

def main():
    # Shared state
    state = {'x': 0.0, 'y': 0.0}
    lock = threading.Lock()

    # Start the input thread
    t = threading.Thread(target=input_thread_fn, args=(state, lock), daemon=True)
    t.start()

    # Wait a moment for you to type the first values
    print("Please enter initial joystick x,y...")
    while True:
        with lock:
            x0, y0 = state['x'], state['y']
        # if either is non-zero (or you can set a flag), break
        if x0 != 0.0 or y0 != 0.0:
            break
        time.sleep(0.1)

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
            turn_scale = 0.5  # Adjust to control turning aggressiveness
            left_factor = 1.0 - turn_scale * x
            right_factor = 1.0 + turn_scale * x
            left_factor = max(0.0, min(1.5, left_factor))
            right_factor = max(0.0, min(1.5, right_factor))
            left_speed = int(speed * left_factor)
            right_speed = int(speed * right_factor)
            left_speed = max(0, min(127, left_speed))
            right_speed = max(0, min(127, right_speed))
            wheel_speeds = [left_speed, right_speed, left_speed, right_speed]

            # Servo angle based on x input
            servo_angle = map_range(x, -1, 1, 0, 255)

            send_rover_command(ser, direction, wheel_speeds, servo_angle)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()