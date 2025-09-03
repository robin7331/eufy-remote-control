
# Flashing MicroPython including LVGL

```bash
git clone https://github.com/lvgl-micropython/lvgl_micropython.git
cd lvgl_micropython
python3 make.py esp32 clean \
  --flash-size=4 \
  --enable-jtag-repl=y \
  BOARD=ESP32_GENERIC_C6 \
  DISPLAY=st7789
esptool.py erase_flash
esptool.py --baud 460800 write_flash 0 build/lvgl_micropy_ESP32_GENERIC_C6-4.bin
```
