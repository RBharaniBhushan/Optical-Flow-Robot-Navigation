# Autonomous Navigation System
# Full navigation with mouse + IMU + Arduino motor control
# Author: R Bharani Bhushan

import evdev
from evdev import InputDevice, ecodes
from mpu6050 import mpu6050
import serial
import threading
import time
import math
import sys
import select

# ─────────────────────────────────────
# CONFIGURATION - Update these values!
# ─────────────────────────────────────
MOUSE_DEVICE = '/dev/input/event0'   # Check with: cat /proc/bus/input/devices
ARDUINO_PORT = '/dev/ttyACM0'        # Check with: ls /dev/ttyACM*
SCALE        = 298.0                 # Units per cm - calibrate for your surface
GX_OFFSET    = -3.0121              # From mpu_calibrate.py
GY_OFFSET    =  2.7723
GZ_OFFSET    =  0.5540
DRIFT_FILTER = 0.5                   # Degrees/sec noise threshold
STOP_RADIUS  = 5.0                   # cm - stopping distance from waypoint

# ─────────────────────────────────────
# SHARED STATE
# ─────────────────────────────────────
pos_x   = 0.0
pos_y   = 0.0
heading = 0.0
lock    = threading.Lock()

# ─────────────────────────────────────
# ARDUINO CONNECTION
# ─────────────────────────────────────
arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
time.sleep(2)
print("Arduino connected!")

def send_cmd(cmd):
    try:
        arduino.write((cmd + '\n').encode())
        time.sleep(0.2)
        if arduino.in_waiting:
            resp = arduino.readline().decode('utf-8', errors='ignore').strip()
            if resp:
                print(f"Arduino: {resp}")
    except Exception as e:
        print(f"\n⚠️ Arduino error: {e}")

# ─────────────────────────────────────
# MOUSE THREAD
# ─────────────────────────────────────
def read_mouse():
    global pos_x, pos_y
    while True:
        try:
            mouse = InputDevice(MOUSE_DEVICE)
            for event in mouse.read_loop():
                if event.type == ecodes.EV_REL:
                    with lock:
                        if event.code == ecodes.REL_X:
                            pos_x += event.value / SCALE
                        if event.code == ecodes.REL_Y:
                            pos_y += event.value / SCALE
        except Exception as e:
            print(f"\n⚠️ Mouse error: {e} — reconnecting...")
            time.sleep(1)

# ─────────────────────────────────────
# IMU THREAD
# ─────────────────────────────────────
def read_imu():
    global heading
    while True:
        try:
            sensor    = mpu6050(0x68)  # Change to 0x69 if needed
            last_time = time.time()
            while True:
                gyro = sensor.get_gyro_data()
                gz   = gyro['z'] - GZ_OFFSET
                if abs(gz) < DRIFT_FILTER:
                    gz = 0
                current_time = time.time()
                dt           = current_time - last_time
                last_time    = current_time
                with lock:
                    heading = (heading + gz * dt) % 360
                time.sleep(0.05)
        except Exception as e:
            print(f"\n⚠️ IMU error: {e} — reconnecting...")
            time.sleep(1)

# ─────────────────────────────────────
# START THREADS
# ─────────────────────────────────────
mouse_thread = threading.Thread(target=read_mouse, daemon=True)
imu_thread   = threading.Thread(target=read_imu,   daemon=True)
mouse_thread.start()
imu_thread.start()
time.sleep(1)

# ─────────────────────────────────────
# NAVIGATION FUNCTION
# ─────────────────────────────────────
def navigate_to(target_x, target_y):
    print(f"\nNavigating to X:{target_x}cm Y:{target_y}cm")

    while True:
        with lock:
            cx = pos_x
            cy = pos_y
            ch = heading

        dx       = target_x - cx
        dy       = target_y - cy
        distance = math.sqrt(dx**2 + dy**2)

        print(f"\rPos X:{cx:.1f} Y:{cy:.1f} | "
              f"Heading:{ch:.1f}° | "
              f"Distance:{distance:.1f}cm    ", end='')

        if distance < STOP_RADIUS:
            send_cmd("S")
            print(f"\n✅ Reached waypoint!")
            break

        target_angle = math.degrees(math.atan2(dx, -dy)) % 360
        angle_error  = target_angle - ch

        if angle_error > 180:
            angle_error -= 360
        if angle_error < -180:
            angle_error += 360

        if abs(angle_error) > 15:
            if angle_error > 0:
                send_cmd("R")
            else:
                send_cmd("L")
        else:
            send_cmd("F")

        time.sleep(0.2)

# ─────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────
waypoints = []

print("\n" + "=" * 50)
print("  Autonomous Navigation System")
print("=" * 50)
print("S → Save waypoint")
print("G → Start autonomous navigation")
print("P → Print waypoints")
print("R → Reset position to 0,0")
print("F → Forward")
print("B → Backward")
print("L → Turn Left")
print("X → Turn Right")
print("T → Stop")
print("Q → Quit\n")

send_cmd("SPD150")

while True:
    with lock:
        cx = round(pos_x, 2)
        cy = round(pos_y, 2)
        ch = round(heading, 1)

    print(f"\rPos → X:{cx:7.2f}cm "
          f"Y:{cy:7.2f}cm "
          f"Heading:{ch:6.1f}°    ", end='')

    if select.select([sys.stdin], [], [], 0)[0]:
        cmd = sys.stdin.read(1).upper()

        if cmd == 'S':
            wp = {'x': cx, 'y': cy}
            waypoints.append(wp)
            print(f"\n✅ Waypoint {len(waypoints)} saved! "
                  f"X:{cx}cm Y:{cy}cm")

        elif cmd == 'G':
            print(f"\n🚀 Starting autonomous navigation!")
            for i, wp in enumerate(waypoints):
                print(f"\nGoing to Point {i+1}...")
                navigate_to(wp['x'], wp['y'])
                print(f"✅ Point {i+1} reached!")
                time.sleep(2)
            print("\n🏁 All waypoints visited!")

        elif cmd == 'P':
            print(f"\n📍 Saved Waypoints:")
            for i, wp in enumerate(waypoints):
                print(f"  Point {i+1} → X:{wp['x']}cm Y:{wp['y']}cm")

        elif cmd == 'R':
            with lock:
                pos_x   = 0.0
                pos_y   = 0.0
                heading = 0.0
            print("\n🔄 Reset to 0,0")

        elif cmd == 'F':
            send_cmd("F")
        elif cmd == 'B':
            send_cmd("B")
        elif cmd == 'L':
            send_cmd("L")
        elif cmd == 'X':
            send_cmd("R")
        elif cmd == 'T':
            send_cmd("S")
        elif cmd == 'Q':
            send_cmd("S")
            arduino.close()
            print("\n👋 Bye!")
            break

    time.sleep(0.1)
