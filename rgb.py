import time

import machine
import neopixel
import _thread

RGB_PIN = 8

RED = (0, 10, 0)
GREEN = (10, 0, 0)
BLUE = (0, 0, 10)
YELLOW = (10, 10, 0)
WHITE = (10, 10, 10)

np = neopixel.NeoPixel(machine.Pin(RGB_PIN), 1)
is_flashing = False
colour = WHITE


def red():
    np[0] = RED
    np.write()


def green():
    np[0] = GREEN
    np.write()


def yellow():
    np[0] = YELLOW
    np.write()


def blue():
    np[0] = BLUE
    np.write()


def white():
    np[0] = WHITE
    np.write()


def off():
    np[0] = (0, 0, 0)
    np.write()


def flash(delay, new_colour):
    global is_flashing, colour

    colour = new_colour

    if is_flashing:
        return

    is_flashing = True
    _thread.start_new_thread(
        _blink_led,
        (delay,),
    )


def stop_flash():
    global is_flashing

    is_flashing = False


def _blink_led(delay):
    global is_flashing, colour

    while is_flashing:
        np[0] = colour
        np.write()
        time.sleep(delay)
        off()
        time.sleep(delay)
