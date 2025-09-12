from machine import PWM, Pin
from asyncio import sleep
from collections import deque
from math import copysign, ceil

class SafeServo:
  ABS_MIN_DUTY = 1638
  ABS_MAX_DUTY = 8192
  ABS_DUTY_RANGE = ABS_MAX_DUTY - ABS_MIN_DUTY

  def __init__(self, pin: Pin, *, safe_min: float=0.0, safe_max: float=1.0):
    """Constructor"""
    # The min, max and range are reversible to allow the servo to be
    # controlled reversed
    self._safe_min = max(min(safe_min, 1.0), 0.0)
    self._safe_max = max(min(safe_max, 1.0), 0.0)
    self._safe_range = self._safe_max - self._safe_min
    # Create the PWM driver for the pin
    self._pos = 0.5
    self._pwm = PWM(pin, freq=50, duty_u16=self._get_pos_pwm(self._pos))

  def _get_pos_pwm(self, safe_pos: float):
    pos = (safe_pos * self._safe_range) + self._safe_min
    return int(pos * self.ABS_DUTY_RANGE) + self.ABS_MIN_DUTY

  @property
  def safe_range(self) -> tuple:
    """Return the servo's safe range as a tuple"""
    return (self._safe_min, self._safe_max)

  @property
  def position(self) -> float:
    """Return the servo safe range position from 0.0 to 1.0"""
    return self._pos

  @position.setter
  def position(self, safe_pos: float) -> None:
    """Set the servo safe range position from 0.0 to 1.0"""
    self._pos = max(min(safe_pos, 1.0), 0.0)
    self._pwm.duty_u16(self._get_pos_pwm(self._pos))


class SmoothServo(SafeServo):
  MAX_SPEED_DEFAULT = 0.35
  MAX_ACCEL_DEFAULT = 0.05
  MAX_STEPS = 200
  
  def __init__(self, pin: Pin, *, safe_min: float=0.0, safe_max: float=1.0,
                  max_speed: float=MAX_SPEED_DEFAULT,
                  max_accel: float=MAX_ACCEL_DEFAULT):
    """Constructor"""
    super().__init__(pin, safe_min=safe_min, safe_max=safe_max)
    self._max_speed = max_speed
    self._max_accel = max_accel
    self._timestep = None
    self._target_pos = self._pos
    self._speed_per_timestep = 0.0
    self._step_pos_list = deque([], self.MAX_STEPS)

  async def run_task(self, ts: int):
    """Async task to advance the servo to the requested position, limiting
    speed and acceleration to the configured limits.
    ts specifies the update timestep."""
    self._timestep = ts
    while True:
      try:
        self._pos, self._speed_per_timestep = self._step_pos_list.popleft()
        self._pwm.duty_u16(self._get_pos_pwm(self._pos))
      except IndexError:
        step_accel = self._max_accel * self._timestep
        if self._pos < (self._target_pos - step_accel) or \
            self._pos > (self._target_pos + step_accel):
          self.position = self._target_pos
          self._pwm.duty_u16(self._get_pos_pwm(self._pos))
        elif self._pos != self._target_pos:
          self._pos = self._target_pos
          self._pwm.duty_u16(self._get_pos_pwm(self._pos))
      await sleep(self._timestep)

  @property
  def position(self) -> float:
    """Return the servo safe range position from 0.0 to 1.0"""
    return self._pos

  @position.setter
  def position(self, target_pos: float) -> None:
    """Set the servo target position from 0.0 to 1.0"""
    # Check if the servo update task is running, bail if not
    if self._timestep is None: return
    # This precalculates the steps needed to get from the current position
    # and the current speed to the target position with zero speed without
    # violating maximum speed and acceleration.
    self._target_pos = max(min(target_pos, 1.0), 0.0)
    start_pos = self._pos
    end_pos = self._target_pos
    delta_pos = end_pos - start_pos
    delta_sign = copysign(1, delta_pos)
    accel = copysign(self._max_accel, delta_pos) * self._timestep
    max_speed = copysign(self._max_speed, delta_pos) * self._timestep
    pos = start_pos
    speed = self._speed_per_timestep
    if speed == 0.0: speed = accel / 2
    pos_list = deque([], self.MAX_STEPS)
    delta_left = end_pos - pos
    # Loop until end position reached
    while (delta_left * delta_sign) > (accel * delta_sign) or \
        abs(speed) >= abs(accel):
      # From our current speed, how many ticks to decelerate to zero?
      stop_ticks = ceil(speed / accel)
      # If we started decelerating now, how far would we travel before
      # we stopped?
      # Fudge it a bit to the high side, that seems to reduce overshoot
      stop_dist = accel * stop_ticks * stop_ticks * 0.5 * 1.1
      # Do we need to start reducing speed to be able to stop?
      if (stop_dist * delta_sign) >= (delta_left * delta_sign):
        # Reduce speed by acceleration every time step
        speed -= accel
      else:
        # Increase speed by acceleration every time step, but limit
        # to the maximum allowed
        speed += accel
        if abs(speed) > abs(max_speed):
          speed = max_speed
      # Adjust position by speed every time step
      pos += speed
      # Save position and speed to the position list
      pos_list.append((pos, speed))
      # Update delta left to target from current position
      delta_left = end_pos - pos
    # Update the list of positions
    self._step_pos_list = pos_list

