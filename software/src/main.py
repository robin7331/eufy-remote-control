import lcd_bus
from micropython import const
import machine
import time


# display settings
_WIDTH = const(172)
_HEIGHT = const(320)
_BL = const(22)
_RST = const(21)
_DC = const(15)

_MOSI = const(6)
_MISO = const(5)
_SCK = const(7)
_HOST = const(1)  # SPI2

_LCD_CS = const(14)
_LCD_FREQ = const(80000000)

_OFFSET_X = const(34)
_OFFSET_Y = const(0)

spi_bus = machine.SPI.Bus(host=_HOST, mosi=_MOSI, miso=_MISO, sck=_SCK)

display_bus = lcd_bus.SPIBus(
    spi_bus=spi_bus,
    freq=_LCD_FREQ,
    dc=_DC,
    cs=_LCD_CS,
)

# we are going to let the display driver sort out the best freame buffer size and where to allocate it to.
# fb1 = display_bus.allocate_framebuffer(_BUFFER_SIZE, lcd_bus.MEMORY_INTERNAL | lcd_bus.MEMORY_DMA)
# fb2 = display_bus.allocate_framebuffer(_BUFFER_SIZE, lcd_bus.MEMORY_INTERNAL | lcd_bus.MEMORY_DMA)

import st7789  # NOQA
import lvgl as lv  # NOQA


display = st7789.ST7789(
    data_bus=display_bus,
    display_width=_WIDTH,
    display_height=_HEIGHT,
    backlight_pin=_BL,
    reset_pin=_RST,
    reset_state=st7789.STATE_HIGH,
    backlight_on_state=st7789.STATE_PWM,
    color_space=lv.COLOR_FORMAT.RGB565,
    color_byte_order=st7789.BYTE_ORDER_RGB,
    rgb565_byte_swap=True,
    offset_x=_OFFSET_X,
    offset_y=_OFFSET_Y,
)

import task_handler  # NOQA

display.set_power(True)
display.reset()
display.init()
display.set_backlight(100)

# Testflächen (falls deine lib fill/rect hat; sonst draw_pixel in Schleife

th = task_handler.TaskHandler()

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

label = lv.label(scrn)
label.set_text("HELLO WORLD!")
label.align(lv.ALIGN.CENTER, 0, 0)
