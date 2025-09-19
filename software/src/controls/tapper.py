from .servo import Servo
import utime


class Tapper:
    def __init__(self, servo_pin=3, retracted_angle=155, extended_angle=118):

        self.retracted_angle = retracted_angle
        self.extended_angle = extended_angle

        # Initialize Servo
        self.servo = Servo(pin_id=servo_pin, max_deg=180, min_deg=0)

        self.last_hold_at = 0
        self.hold_duration = 0

    def tap(self, hold_duration=1000):
        if self.last_hold_at > 0:
            return
        self.hold_duration = hold_duration
        self.last_hold_at = utime.ticks_ms()
        self.servo.write(self.extended_angle)

    def tick(self):
        if (
            self.last_hold_at > 0
            and (utime.ticks_ms() - self.last_hold_at) >= self.hold_duration
        ):
            self.last_hold_at = 0
        elif self.last_hold_at == 0:
            self.servo.write(self.retracted_angle)
