# Optical Flow Robot Navigation

A low-cost autonomous robot navigation system using a USB optical mouse sensor for position tracking and MPU6050 IMU for heading detection, implemented on Raspberry Pi 3B.

## Overview
This project implements autonomous waypoint navigation for a differential drive robot without requiring GPS, SLAM or floor markings. A standard USB laser mouse is repurposed as an optical flow sensor mounted under the robot chassis to track X/Y displacement in real time. An MPU6050 IMU provides heading estimation through gyroscope integration enabling accurate turning.

## Features
- Real time 2D position tracking using USB optical mouse sensor
- Heading detection using MPU6050 IMU with gyroscope calibration
- Waypoint recording by manually driving robot and saving positions
- Autonomous navigation toward saved waypoints using distance and heading correction
- Auto reconnect logic for sensor disconnection handling
- Motor control via Arduino Uno over USB serial communication
- Live path visualization using pygame

## Hardware Requirements
- Raspberry Pi 3B
- USB laser/optical mouse
- MPU6050 IMU sensor
- Arduino Uno
- L298N motor driver
- 4WD robot chassis with DC geared motors
- 4S Li-ion battery pack
- LM2596 buck converter

## Software Requirements
- Raspberry Pi OS
- Python 3.11
- evdev library
- mpu6050-raspberrypi library
- pyserial library
- pygame library

## Installation
```bash
sudo pip3 install evdev mpu6050-raspberrypi pyserial pygame --break-system-packages
```

## Hardware Setup
### Mouse Sensor
- Mount USB mouse upside down under chassis center
- Maintain 2-3mm gap from ground surface
- Connect to Raspberry Pi USB port

### MPU6050 Wiring
```
MPU6050    →    Raspberry Pi
VCC        →    Pin 1 (3.3V)
GND        →    Pin 6 (GND)
SDA        →    Pin 3 (GPIO2)
SCL        →    Pin 5 (GPIO3)
```

### Arduino to Raspberry Pi
```
Arduino USB → Raspberry Pi USB port (/dev/ttyACM0)
```

### L298N to Arduino
```
ENA → Pin 11 (PWM)
IN1 → Pin 10
IN2 → Pin 9
IN3 → Pin 8
IN4 → Pin 7
ENB → Pin 6 (PWM)
```

## Calibration
### Mouse Scale Factor
```bash
sudo python3 mouse_test.py
```
Push robot exactly 10cm and note Y value:
```
Scale = Y value / 10
```
Update SCALE in agribot_nav.py accordingly.

### IMU Calibration
```bash
sudo python3 mpu_calibrate.py
```
Keep sensor completely still for 5 seconds. Note offset values and update in agribot_nav.py.

## Usage
### Step 1 — Check all devices detected
```bash
ls /dev/input/event*
sudo i2cdetect -y 1
ls /dev/ttyACM*
```

### Step 2 — Run navigation system
```bash
sudo python3 agribot_nav.py
```

### Step 3 — Record waypoints
- Drive robot manually to each plant position
- Press **S** to save each waypoint
- Press **P** to print all saved waypoints

### Step 4 — Autonomous navigation
- Bring robot back to start position
- Press **R** to reset position
- Press **G** to start autonomous navigation

## Commands
| Key | Action |
|-----|--------|
| S | Save current position as waypoint |
| G | Start autonomous navigation |
| P | Print all waypoints |
| R | Reset position to 0,0 |
| F | Move forward |
| B | Move backward |
| L | Turn left |
| X | Turn right |
| T | Stop |
| Q | Quit |

## Scale Factor
Calibrated scale factor: **298 units per cm** on smooth floor surface.

## How It Works
```
USB Mouse → Tracks X/Y displacement (position)
MPU6050   → Tracks Z-axis gyroscope (heading)
Combined  → Full 2D position and orientation tracking
Arduino   → Motor control via serial commands
Pi        → Navigation logic and waypoint management
```

## Navigation Algorithm
1. Calculate Euclidean distance to target waypoint
2. Calculate required heading angle toward target
3. If heading error > 15° → turn left or right
4. If heading error < 15° → move forward
5. If distance < 5cm → stop, waypoint reached

## Project Structure
```
Optical-Flow-Robot-Navigation/
├── README.md
├── raspberry_pi/
│   ├── agribot_nav.py      ← Main navigation system
│   ├── mouse_test.py       ← Mouse sensor test
│   ├── mpu_heading.py      ← IMU heading test
│   ├── mpu_calibrate.py    ← IMU calibration
│   └── navigation.py       ← Waypoint recorder
└── arduino/
    └── motor_control.ino   ← Arduino motor control
```

## Results
- Mouse sensor scale factor: 298 units/cm
- IMU heading accuracy: ~88° on 90° rotation (2.2% error)
- Waypoint navigation demonstrated successfully on chassis

## Future Improvements
- Implement Kalman filter for sensor fusion
- Add encoder based odometry for improved accuracy
- Integrate with disease detection pipeline
- Support for multi-row U-shaped navigation path

## License
MIT License

## Author
R Bharani Bhushan
B.Tech EEE, M.S. Ramaiah University of Applied Sciences
