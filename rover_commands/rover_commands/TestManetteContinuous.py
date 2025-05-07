import serial
import time

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
    # Initialize serial
    ser = serial.Serial('/dev/pts/1', 9600, timeout=1)
    time.sleep(2)

    # Default joystick values
    x, y = 0.0, 0.0

    try:
        while True:
            # Prompt for new input (optional)
            print("\n--- Update Joystick ---")
            print("Press Enter to keep current joystick values.")
            user_input = input(f"Joystick x axis (-1.0 to 1.0) [current: {x}]: ")
            if user_input.strip() != "":
                x = float(user_input)
                x = max(-1.0, min(1.0, x))

            user_input = input(f"Joystick y axis (-1.0 to 1.0) [current: {y}]: ")
            if user_input.strip() != "":
                y = float(user_input)
                y = max(-1.0, min(1.0, y))

            # Keep sending current values until user wants to change them
            print("Sending current joystick state repeatedly... (Ctrl+C to interrupt)")
            while True:
                direction = 0 if y >= 0 else 1
                speed = map_range(abs(y), 0, 1, 0, 127)

                # Turning logic
                turn_scale = 0.5
                left_factor = 1.0 - turn_scale * x
                right_factor = 1.0 + turn_scale * x
                left_factor = max(0.0, min(1.5, left_factor))
                right_factor = max(0.0, min(1.5, right_factor))
                left_speed = int(speed * left_factor)
                right_speed = int(speed * right_factor)
                left_speed = max(0, min(127, left_speed))
                right_speed = max(0, min(127, right_speed))
                wheel_speeds = [left_speed, right_speed, left_speed, right_speed]

                servo_angle = map_range(x, -1, 1, 0, 255)

                send_rover_command(ser, direction, wheel_speeds, servo_angle)
                time.sleep(0.1)

                # Check if the user wants to break the loop to enter new values
                if ser.in_waiting:
                    break  # optional: add a way to signal exit
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        ser.close()