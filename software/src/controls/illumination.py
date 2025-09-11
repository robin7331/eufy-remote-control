import utime
import math


class Illumination:
    def __init__(self, led_indexes=[], on_should_render=None, lerp_speed=0.25):
        self.on_should_render = on_should_render
        self.lerp_speed = lerp_speed
        self.on_should_render = on_should_render
        self.last_animated_at = 0
        self.lerp_speed = lerp_speed
        self.pulsing = False
        self.pulse_from_color = None
        self.pulse_from_brightness = None
        self.pulse_to_color = None
        self.pulse_to_Brightness = None
        self.pulseDirection = 0
        self.color = (0, 0, 0, 0.0)
        self.led_indexes = led_indexes
        self.target_color = self.color
        self.flash_active = False
        self.flash_start_time = 0
        self.flash_duration = 0
        self.flash_animated = True
        self.flash_original_color = (0, 0, 0, 0.0)

                                     

    def tick(self):
        # Handle flash logic
        if self.flash_active:
            elapsed = utime.ticks_ms() - self.flash_start_time
            if elapsed >= self.flash_duration:
                # Restore original color
                orig = getattr(self, 'flash_original_color', (0, 0, 0, 0.0))
                self.set_color((orig[0], orig[1], orig[2]), orig[3], animated=self.flash_animated)
                self.flash_active = False

        if self.pulsing:
            # Pulse to?
            if self.pulseDirection is 1:
                self.set_color(self.pulse_to_color, self.pulse_to_Brightness)
                if self.is_color_set(source_color=self.pulse_to_color, source_brightness=self.pulse_to_Brightness):
                    self.pulseDirection = 2
            elif self.pulseDirection is 2:
                self.set_color(self.pulse_from_color, self.pulse_from_brightness)
                if self.is_color_set(source_color=self.pulse_from_color, source_brightness=self.pulse_from_brightness):
                    self.pulseDirection = 1

        wait_time = (1000//30) - (utime.ticks_ms() - self.last_animated_at)
        if wait_time <= 0:
            self.last_animated_at = utime.ticks_ms()
            self.__animate()

    def __animate(self):
        self.color = self.__lerpColor(self.color, self.target_color)
        if self.on_should_render:
            self.on_should_render(self)

    def __lerpColor(self, current, target):
        return (current[0] + int((target[0] - current[0]) * self.lerp_speed), current[1] + int((target[1] - current[1]) * self.lerp_speed), current[2] + int((target[2] - current[2]) * self.lerp_speed), current[3] + (target[3] - current[3]) * self.lerp_speed)

    def set_color(self, color, brightness, animated=True):
        if not animated:
            self.target_color = self.color = (
                color[0], color[1], color[2], brightness)
            return

        self.target_color = (color[0], color[1], color[2], brightness)

    def clear_color(self, animated=True):
        if not animated:
            self.target_color = self.color = (0, 0, 0, 0.0)
            return

        self.target_color = (0, 0, 0, 0.0)

    def pulsate(self, fromColor, fromBrightness, toColor, toBrightness):
        self.pulsing = True
        self.pulseDirection = 1
        self.pulse_from_color = fromColor
        self.pulse_from_brightness = fromBrightness
        self.pulse_to_color = toColor
        self.pulse_to_Brightness = toBrightness

    def stop_pulsating(self, to_color=(0, 0, 0), to_brightness=0.0):
        self.pulsing = False
        self.pulseDirection = 0
        self.pulse_from_color = None
        self.pulse_from_brightness = None
        self.pulse_to_color = None
        self.pulse_to_Brightness = None
        self.target_color = (to_color[0], to_color[1], to_color[2], to_brightness)

    def flash(self, color, brightness, from_color=None, duration=500):
        if self.flash_active:
            return
        
        # Save the current color and brightness
        if from_color:
            self.flash_original_color = (from_color[0], from_color[1], from_color[2], brightness)
        else:
            self.flash_original_color = (self.color[0], self.color[1], self.color[2], self.color[3])
        
        self.flash_active = True
        self.flash_start_time = utime.ticks_ms()
        self.flash_duration = duration
        self.set_color(color, brightness, False)


    def is_color_set(self, source_color, source_brightness, colorMargin=10, brightnessMargin=0.01):
        for i in range(2):
            if abs(source_color[i]-self.color[i]) > colorMargin:
                return False

        if math.fabs(source_brightness-self.color[3]) > brightnessMargin:
            return False

        return True
