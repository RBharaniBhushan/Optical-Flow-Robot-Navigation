# MPU6050 IMU Calibration
# Calculates gyroscope offsets for accurate heading tracking
# Author: R Bharani Bhushan

from mpu6050 import mpu6050
import time

sensor = mpu6050(0x68)  # Change to 0x69 if needed

print("MPU6050 Calibration")
print("Keep sensor COMPLETELY STILL for 5 seconds!\n")
time.sleep(2)

samples = 200
gx_offset = 0
gy_offset = 0
gz_offset = 0

for i in range(samples):
    gyro = sensor.get_gyro_data()
    gx_offset += gyro['x']
    gy_offset += gyro['y']
    gz_offset += gyro['z']
    time.sleep(0.01)

gx_offset /= samples
gy_offset /= samples
gz_offset /= samples

print(f"Calibration Complete!")
print(f"Gyro Offsets:")
print(f"  X offset: {gx_offset:.4f}")
print(f"  Y offset: {gy_offset:.4f}")
print(f"  Z offset: {gz_offset:.4f}")
print(f"\nUpdate these values in agribot_nav.py!")

# Test with offsets applied
print("\nTesting with calibration (keep still - values should be ~0)\n")
time.sleep(2)

while True:
    gyro = sensor.get_gyro_data()
    gx = gyro['x'] - gx_offset
    gy = gyro['y'] - gy_offset
    gz = gyro['z'] - gz_offset
    print(f"Gyro (calibrated) → X: {gx:6.2f}  Y: {gy:6.2f}  Z: {gz:6.2f}")
    time.sleep(0.2)
