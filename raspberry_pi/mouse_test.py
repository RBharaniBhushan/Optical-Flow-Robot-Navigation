# Mouse Sensor Test
# Tests USB optical mouse position tracking on Raspberry Pi
# Author: R Bharani Bhushan

import evdev
from evdev import InputDevice, ecodes

# Mouse device - change event number if needed
mouse = InputDevice('/dev/input/event0')

print("Mouse tracking started! Move the mouse...")
print("Press Ctrl+C to stop\n")

total_x = 0
total_y = 0

for event in mouse.read_loop():
    if event.type == ecodes.EV_REL:
        if event.code == ecodes.REL_X:
            total_x += event.value
        if event.code == ecodes.REL_Y:
            total_y += event.value

        print(f"Movement → X: {event.value if event.code == 0 else 0:+4d}   "
              f"Y: {event.value if event.code == 1 else 0:+4d}   "
              f"| Total Position → X: {total_x:6d}  Y: {total_y:6d}")
