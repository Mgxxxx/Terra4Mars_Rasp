import serial
import time

#test
def main():
    # Set up the serial connection to the Arduino
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)  # Adjust '/dev/ttyUSB0' to your serial port
    time.sleep(2)  # Allow time for the Arduino to reset
    c = 0

    print("Enter 0 (forwards) or 1 (backwards):")
    try:
        while True:
            command = input("Command: ").strip()
            if c == 0:
                ser.write(command.encode('utf-8'))  # Send the command as a byte
                print(f"Sent command: {command}")
            else:
                print("Invalid command. Please enter 0 or 1.")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()