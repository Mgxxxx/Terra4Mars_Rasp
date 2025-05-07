import serial
import time
import math

# Config
SERIAL_PORT = '/dev/pts/2'  # opposite of the sender port
MAX_SPEED = 0.3  # meters/sec
SERVO_MIN_DEG = -30
SERVO_MAX_DEG = 30

# State
x, y = 0.0, 0.0
last_update_time = time.time()

def estimate(wheel_speeds, servo_angle, dt, direction):
    global x, y

    avg_pwm = sum(wheel_speeds) / 4.0
    sign = 1 if direction == 0 else -1
    speed = sign * (avg_pwm / 127.0) * MAX_SPEED

    angle_deg = (servo_angle / 255.0) * (SERVO_MAX_DEG - SERVO_MIN_DEG) + SERVO_MIN_DEG
    angle_rad = math.radians(angle_deg)

    dx = speed * math.cos(angle_rad) * dt
    dy = speed * math.sin(angle_rad) * dt
    x += dx
    y += dy

    print(f"[Est] Pos: ({x:.2f}, {y:.2f}) m | Speed: {speed:.2f} m/s | Angle: {angle_deg:.1f}°")

def main():
    ser = serial.Serial(SERIAL_PORT, 9600)
    print("Listening for control packets...")

    last_time = time.time()
    while True:
        if ser.in_waiting >= 7:
            start = ser.read(1)
            if start[0] != 0x31:
                continue  # skip invalid packets

            data = ser.read(6)
            direction = data[0]
            wheel_speeds = list(data[1:5])
            servo_angle = data[5]

            now = time.time()
            dt = now - last_time
            last_time = now

            estimate(wheel_speeds, servo_angle, dt, direction)

if __name__ == "__main__":
    main()