import math
import time

def update_position(wheel_speeds, servo_angle):
    # Constants
    MAX_SPEED = 0.3  # meters/second when PWM = 127
    SERVO_MIN_DEG = -30
    SERVO_MAX_DEG = 30
    UPDATE_INTERVAL = 0.5  # seconds

    # Position tracking variables
    x, y = 0.0, 0.0
    last_update_time = time.time()

    now = time.time()
    dt = now - last_update_time
    if dt < UPDATE_INTERVAL:
        return  # not time yet

    # Convert wheel speeds to average speed
    avg_pwm = sum(wheel_speeds) / 4.0
    speed = (avg_pwm / 127.0) * MAX_SPEED

    # Convert servo angle (0–255) to degrees
    angle_deg = (servo_angle / 255.0) * (SERVO_MAX_DEG - SERVO_MIN_DEG) + SERVO_MIN_DEG
    angle_rad = math.radians(angle_deg)

    # Update position
    dx = speed * math.cos(angle_rad) * dt
    dy = speed * math.sin(angle_rad) * dt
    x += dx
    y += dy
    last_update_time = now

    print(f"[Est] Pos: ({x:.2f}, {y:.2f}) m | Speed: {speed:.2f} m/s | Angle: {angle_deg:.1f}°")