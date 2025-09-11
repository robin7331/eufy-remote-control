import array
from machine import Pin
import rp2


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW, out_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    # 1 step = 0.2us (clock frequency must be set to 5MHz)
    wrap_target()
    # 1 step at 0 (to wait for data in low state, reset code)
    out(x, 1)
    # start of the cycle
    # 2 step at 1
    set(pins, 1) [1]
    # 2 step at x
    mov(pins, x) [1]
    # 1 step at 0
    set(pins, 0)
    wrap()
 


class UIRenderer:
    def __init__(self, on_rendering_finished=None, led_pin=6, led_count=4, brightness_modifier=1.0):
        self.on_rendering_finished = on_rendering_finished
        self.led_count = led_count
        self.is_dirty = True
        self.brightness_modifier = brightness_modifier

        # Basically our frame buffer
        self.pixel_array = array.array("I", [0 for _ in range(self.led_count)])
        self.brightness_array = array.array(
            "f", [0 for _ in range(self.led_count)])

        # Create the StateMachine with the ws2812 program.
        # Its running at 8MHz so it has 10 clock cycles and outputs data with 800kHz just as the WS2812 spec says.
        self.state_machine = rp2.StateMachine(0, ws2812, freq=5_000_000, set_base=Pin(led_pin), out_base=Pin(led_pin))
        self.state_machine.active(1)

    def flush_frame_buffer(self):
        if not self.is_dirty:
            return

        dimmer_array = array.array("I", [0 for _ in range(self.led_count)])
        for index, pixelValue in enumerate(self.pixel_array):
            brightness = self.brightness_array[index]
            # 8-bit red dimmed to brightness
            r = int(((pixelValue >> 8) & 0xFF) *
                    brightness * self.brightness_modifier)
            # 8-bit green dimmed to brightness
            g = int(((pixelValue >> 16) & 0xFF) *
                    brightness * self.brightness_modifier)
            # 8-bit blue dimmed to brightness
            b = int((pixelValue & 0xFF) * brightness *
                    self.brightness_modifier)
            # 24-bit color dimmed to brightness
            dimmer_array[index] = (g << 16) + (r << 8) + b

        # update the state machine with new colors
        self.state_machine.put(dimmer_array, 8)
        self.is_dirty = False

        if self.on_rendering_finished:
            self.on_rendering_finished()

    def set_led_color(self, index, color, brightness=1.0):
        self.is_dirty = True
        self.pixel_array[index] = (color[1] << 16) + (color[0] << 8) + color[2]
        self.brightness_array[index] = brightness
