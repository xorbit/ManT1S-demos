from machine import Pin, SPI, ADC, reset
from servo import SmoothServo
from camera import Camera


# SPI for ArduCam Mega on the default SPI1 pins:
# MISO: IO12
# MOSI: IO13
# SCK: IO14
arducam_spi = SPI(1, 8000000)
arducam_cs = Pin(15, Pin.OUT)
# Camera driver
cam = Camera(arducam_spi, arducam_cs)

# Create servo objects
wrist_tilt_servo = SmoothServo(Pin(2), safe_min=1.0, safe_max=0.0)
wrist_rotate_servo = SmoothServo(Pin(4), max_speed=2.0, max_accel=0.2)
claw_servo = SmoothServo(Pin(20), safe_min=0.35, safe_max=0.9,
                          max_speed=2.0, max_accel=0.2)

# Claw pressure sensor ADCs
# Input range 0.15 ~ 2.45 V
claw_pressure_adc = (
  ADC(Pin(36), atten=ADC.ATTN_11DB),
  ADC(Pin(37), atten=ADC.ATTN_11DB)
)


