from machine import Pin, reset
from servo import SmoothServo

# Create servo objects
shoulder_rotate_servo = SmoothServo(Pin(2), safe_min=1.0, safe_max=0.0)
shoulder_tilt_servo = SmoothServo(Pin(4))
elbow_servo = SmoothServo(Pin(20), safe_min=1.0, safe_max=0.0)

