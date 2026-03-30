# MPU6050 Heading Tracker
# Tracks robot heading using IMU gyroscope integration
# Author: R Bharani Bhushan

from mpu6050 import mpu6050
import time

sensor = mpu6050(0x68)  # Change to 0x69 if needed

# Calibration offsets - update after running mpu_calibrate.py
GX_OFFSET = -3.0121
GY_OFFSET =  2.7723
GZ_OFFSET =  0.5540
DRIFT_FILTER = 0.5  # degrees/sec threshold

heading   = 0.0
last_time = time.time()

print("Heading Tracker Started!")
print("Rotate the sensor and watch heading change...")
print("Press Ctrl+C to stop\n")

while True:
    gyro = sensor.get_gyro_data()
    gz   = gyro['z'] - GZ_OFFSET

    if abs(gz) < DRIFT_FILTER:
        gz = 0

    current_time = time.time()
    dt           = current_time - last_time
    last_time    = current_time

    heading = (heading + gz * dt) % 360

    print(f"Heading: {heading:6.1f}°  |  Gyro Z: {gz:6.2f}", end='\r')
    time.sleep(0.05)
