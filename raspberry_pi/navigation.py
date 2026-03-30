# Waypoint Navigation System
# Records and displays waypoints using mouse + IMU
# Author: R Bharani Bhushan

import evdev
from evdev import InputDevice, ecodes
from mpu6050 import mpu6050
import threading
import time
import sys
import select

# ─────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────
MOUSE_DEVICE = '/dev/input/event0'
SCALE        = 298.0   # mouse units per cm - recalibrate for your surface
GX_OFFSET    = -3.0121
GY_OFFSET    =  2.7723
GZ_OFFSET    =  0.5540
DRIFT_FILTER = 0.5

# ─────────────────────────────────────
# SHARED STATE
# ─────────────────────────────────────
pos_x   = 0.0
pos_y   = 0.0
heading = 0.0
lock    = threading.Lock()

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
            sensor    = mpu6050(0x68)
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
# MAIN MENU
# ─────────────────────────────────────
waypoints = []

print("=" * 50)
print("  Waypoint Navigation System")
print("=" * 50)
print("S → Save waypoint")
print("P → Print waypoints")
print("R → Reset position")
print("Q → Quit\n")

while True:
    with lock:
        cx = round(pos_x, 2)
        cy = round(pos_y, 2)
        ch = round(heading, 1)

    print(f"\rPosition → X: {cx:7.2f}cm  "
          f"Y: {cy:7.2f}cm  "
          f"Heading: {ch:6.1f}°    ", end='')

    if select.select([sys.stdin], [], [], 0)[0]:
        cmd = sys.stdin.read(1).upper()

        if cmd == 'S':
            wp = {'x': cx, 'y': cy, 'heading': ch}
            waypoints.append(wp)
            print(f"\n✅ Waypoint {len(waypoints)} saved! "
                  f"X:{cx}cm Y:{cy}cm Heading:{ch}°")

        elif cmd == 'P':
            print(f"\n📍 Saved Waypoints:")
            for i, wp in enumerate(waypoints):
                print(f"  Point {i+1} → "
                      f"X:{wp['x']}cm  "
                      f"Y:{wp['y']}cm  "
                      f"Heading:{wp['heading']}°")

        elif cmd == 'R':
            with lock:
                pos_x   = 0.0
                pos_y   = 0.0
                heading = 0.0
            print("\n🔄 Position reset to 0,0")

        elif cmd == 'Q':
            print("\n👋 Bye!")
            break

    time.sleep(0.1)
