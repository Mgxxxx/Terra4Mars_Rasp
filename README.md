# Terra4Mars Rover Control

Wireless control system for the EPFL Xplore mini rover. Translates PS4 controller input into differential drive motor commands over UDP/serial.

## Architecture

```
┌─────────────────┐      UDP       ┌─────────────────┐     Serial     ┌─────────────┐
│   Host (PC)     │  ──────────►   │  Raspberry Pi   │  ──────────►   │   Arduino   │
│   sender.py     │   port 9999    │  receiver.py    │   /dev/ttyUSB0 │   (motors)  │
└─────────────────┘                └─────────────────┘                └─────────────┘
       │
       │ pygame
       ▼
 ┌─────────────┐
 │ PS4 DualShock│
 └─────────────┘
```

**Standalone mode**: For direct USB connection (no network), use `controller.py` which combines joystick reading and serial output on a single machine.

## Protocol

6-byte packet: `[0xFF, L1, R1, L2, R2, SERVO]`

| Byte | Description |
|------|-------------|
| 0 | Start marker (0xFF) |
| 1-4 | Wheel speeds. Bit 7: direction (0=fwd, 1=rev). Bits 0-6: speed (0-127) |
| 5 | Servo angle (0-255 → full left to full right) |

Differential steering: left stick X modulates left/right wheel speed ratio. Left stick Y controls base speed and direction.

## Setup

**Dependencies**: Python 3.8+, pygame, pyserial

```bash
pip install pygame pyserial
```

**Raspberry Pi**: Ensure `/dev/ttyUSB0` permissions or add user to `dialout` group.

## Usage

### Wireless (Host + Pi)

1. On Raspberry Pi:
   ```bash
   python rover_commands/raspberry/receiver.py
   ```

2. On host machine (with PS4 controller connected):
   ```bash
   python rover_commands/host/sender.py
   ```

Edit `PI_IP` in `sender.py` to match your Pi's address.

### Standalone (Direct Serial)

```bash
python rover_commands/rover_commands/controller.py
```

### Docker

```bash
cd docker
./build.sh    # or build.bat on Windows
./run.sh      # or run.bat on Windows
```

## Configuration

Key parameters in each module:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SERIAL_PORT` | `/dev/ttyUSB0` | Arduino serial device |
| `BAUDRATE` | 9600 | Serial baud rate |
| `PI_IP` | `172.20.10.2` | Raspberry Pi IP (sender only) |
| `PI_PORT` | 9999 | UDP port |
| `DEADZONE` | 0.05-0.1 | Joystick deadzone |
| `TURN_SCALE` | 0.5-0.6 | Steering sensitivity |

## Project Structure

```
├── rover_commands/
│   ├── host/
│   │   └── sender.py          # UDP sender (runs on PC)
│   ├── raspberry/
│   │   └── receiver.py        # UDP→serial bridge (runs on Pi)
│   └── rover_commands/
│       └── controller.py      # Standalone controller
├── docker/
│   ├── Dockerfile
│   ├── build.sh / build.bat
│   └── run.sh / run.bat
└── README.md
```

## License

MIT
