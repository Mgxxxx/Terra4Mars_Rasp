import pygame
import socket
import time
import os

# Tell SDL there is no real display (headless)
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    raise RuntimeError("No joystick found")

js = pygame.joystick.Joystick(0)
js.init()
print("Using joystick:", js.get_name())

# Network setup
PI_IP   = "172.20.10.2"   # ← Change to your Pi’s IP
PI_PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Map range helper
def map_range(v, a, b, c, d):
    return int((v - a) * (d - c) / (b - a) + c)

try:
    while True:
        pygame.event.pump()
        raw_x = js.get_axis(0)   # Left stick X
        raw_y = -js.get_axis(1)  # Left stick Y, invert so up is +1

        # Dead-zone
        if abs(raw_x) < 0.05: raw_x = 0.0
        if abs(raw_y) < 0.05: raw_y = 0.0

        direction = 0 if raw_y >= 0 else 1
        speed     = map_range(abs(raw_y), 0, 1, 0, 127)

        turn_scale = 0.6
        lf = max(0, min(1.5, 1 - turn_scale * raw_x))
        rf = max(0, min(1.5, 1 + turn_scale * raw_x))

        lspd = max(0, min(127, int(speed * lf)))
        rspd = max(0, min(127, int(speed * rf)))

        # pack direction into the speeds as before
        wheels = [
            lspd + direction * 127,
            rspd + direction * 127,
            lspd + direction * 127,
            rspd + direction * 127,
        ]

        servo = map_range(raw_x, -1, 1, 0, 255)

        # Build the exact byte packet:
        packet = bytearray([255])          # start marker
        packet.extend(wheels)              # 4 bytes
        packet.append(servo)               # 1 byte

        # Send to Pi
        sock.sendto(packet, (PI_IP, PI_PORT))

        # Optional: print for debug
        print("Sent", [hex(b) for b in packet])

        time.sleep(0.05)  # 20 Hz send rate
except KeyboardInterrupt:
    print("Sender stopped")
finally:
    js.quit()
    pygame.quit()
    sock.close()