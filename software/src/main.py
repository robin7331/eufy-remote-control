import machine

from time import sleep
import machine
import ujson
from ui_renderer import UIRenderer
from boot_sequence import run_boot_sequence
from machine import Timer
import utime
from controls.io_event_source import IOEventSource
from controls.io_event import IOEvent
from controls.illumination import Illumination
from controls.tapper import Tapper
from device import Device
from connection_manager import ConnectionManager, ConnectionState, PingState
import asyncio


# MQTT Broker details
BROKER_IP = '192.168.4.167'
BROKER_PORT = 1883
STATUS_TOPIC = 'uv_studio/status'
COMMAND_TOPIC = 'uv_studio/command'
CONTROL_TOPIC = 'uv_studio/control'

machine.freq(96000000)

# The UI Renderer class holds the frame buffer and the PIO state machine
renderer = UIRenderer(brightness_modifier=1.0, led_pin=6, led_count=8)



# Lets render the buttons at 30 fps (just for the boot sequence)
uiTimer = Timer()
uiTimer.init(freq=30, mode=Timer.PERIODIC,
             callback=lambda t: renderer.flush_frame_buffer())
# # Lets run a fancy rainbow boot sequence
run_boot_sequence(renderer, led_count=8, brightness=0.8)
uiTimer.deinit()


def renderIllumination(entity):
    global renderer
    for led_index in entity.led_indexes:
        renderer.set_led_color(
            led_index, (entity.color[0], entity.color[1], entity.color[2]), entity.color[3])

left_button_illumination = Illumination(led_indexes=[4,5,6,7], on_should_render=renderIllumination)    
right_button_illumination = Illumination(led_indexes=[0,1,2,3], on_should_render=renderIllumination)    

left_button_illumination.set_color((0, 0, 0), 0.0, animated=False)
right_button_illumination.set_color((0, 0, 0), 0.0, animated=False)

tapper = Tapper()

device = Device(left_illumination=left_button_illumination, right_illumination=right_button_illumination, tapper=tapper)



def connection_cb(connection_manager, state):
    print('Connection state changed to: %s' % state)
    if state is ConnectionState.ERROR:
        device.to_error()

def on_ping(connection_manager, state):
    print('Ping state changed to: %s' % state)
    if state is PingState.PRINTING_12MM:
        device.to_printing(type='12mm')

    if state is PingState.PRINTING_16MM:
        device.to_printing(type='16mm')

    if state is PingState.ERROR_12MM:
        device.to_error(type='12mm')

    if state is PingState.ERROR_16MM:
        device.to_error(type='16mm')

    if state is PingState.TIMEOUT:
        device.to_timeout()

    if state is PingState.IDLE: 
        device.to_idle()


def left_button_tapped(source):
    global connection_manager
    if device.is_idle() or device.is_error():
        connection_manager.send_mqtt_command('start_12mm_print')
    else: 
        print('Not in idle state, ignoring button press')


def right_button_tapped(source):
    global connection_manager
    if device.is_idle() or device.is_error():
        connection_manager.send_mqtt_command('start_16mm_print')
    else: 
        print('Not in idle state, ignoring button press')

def stop(source):
    global connection_manager
    connection_manager.send_mqtt_command('stop')

def set_tapper_parameters(retracted_angle, extended_angle):
    tapper.retracted_angle = retracted_angle
    tapper.extended_angle = extended_angle


left_button = IOEventSource(title='Left Button', pin_number=4, pin_mode=machine.Pin.IN, pin_pull=machine.Pin.PULL_UP, invert=True, on_tapped=left_button_tapped, on_long_hold=stop)
right_button = IOEventSource(title='Right Button', pin_number=5, pin_mode=machine.Pin.IN, pin_pull=machine.Pin.PULL_UP, invert=True, on_tapped=right_button_tapped, on_long_hold=stop)

connection_manager = ConnectionManager(BROKER_IP, BROKER_PORT)
connection_manager.set_on_connection_changed(connection_cb)
connection_manager.set_on_trigger_servo(lambda: tapper.tap())
connection_manager.set_on_ping_changed(on_ping)
connection_manager.set_on_servo_parameters_received(set_tapper_parameters)

asyncio.run(connection_manager.connect())

# We are ready!
left_button_illumination.flash((0, 255, 0), 0.28)
right_button_illumination.flash((0, 255, 0), 0.28)

last_rendered_at = utime.ticks_ms()

while True:       
    left_button.tick()
    left_button_illumination.tick()

    right_button.tick()
    right_button_illumination.tick()

    device.tick(utime.ticks_ms())

    connection_manager.tick()

    tapper.tick()

    # Render the UI at 30 FPS.
    if utime.ticks_ms() - last_rendered_at > 33:
        renderer.flush_frame_buffer()
        last_rendered_at = utime.ticks_ms()

