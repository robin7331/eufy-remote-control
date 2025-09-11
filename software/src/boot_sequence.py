import utime

def wheel(pos):
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def run_boot_sequence(renderer, led_count=4, brightness=1.0):
    for i in range(255):
        b = (i / 255) * brightness
        for j in range(led_count):
            rc_index = (j * 256 // led_count) + i
            renderer.set_led_color(j, wheel(rc_index & 255), b)
            utime.sleep_us(100)
    for i in range(255):
        b = brightness - ((i / 255) * brightness)
        for j in range(led_count):
            rc_index = (j * 256 // led_count) + i
            renderer.set_led_color(j, wheel(rc_index & 255), b)
            utime.sleep_us(100)
