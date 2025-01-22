import time

import machine

# H-Bridge DC motor controller:
#
#                 12V
#                  |
#        +-------------------+
#        |                   |
#    [Relay 1]          [Relay 2]
#        |                   |
#        +------ MOTOR ------+
#        |                   |
#    [Relay 3]          [Relay 4]
#        |                   |
#        +-------------------+
#                  |
#                 GND
#
# Relay 1 & 2 are Normally Opened.
# Relay 3 & 4 are Normally Closed.
#

GROUND_DURATION = 100  # ms

last_motor_ground_time = 0

RELAY_1_PIN = 14
RELAY_2_PIN = 15
RELAY_3_PIN = 18
RELAY_4_PIN = 19

relay_1 = machine.Pin(RELAY_1_PIN, machine.Pin.OUT)
relay_2 = machine.Pin(RELAY_2_PIN, machine.Pin.OUT)
relay_3 = machine.Pin(RELAY_3_PIN, machine.Pin.OUT)
relay_4 = machine.Pin(RELAY_4_PIN, machine.Pin.OUT)


def stop():
    """
    Stop the motor.

    Blocking sleep after coasting as we aren't interested in
    responding to inputs so quickly when the motor is changing
    direction.
    """
    _coast_motor()
    time.sleep(1)
    _ground_motor()


def _coast_motor():
    """
    Coast the motor by just opening the top relays. Keeping one of the bottom relays closed.
    """
    print("--- Coasting motor --- ")
    relay_1.value(0)
    relay_2.value(0)


def _ground_motor():
    """
    Ground the motor by resetting the outputs, by default the motor is grounded.
    """
    global last_motor_ground_time

    print("--- Grounding motor ---")

    now = time.ticks_ms()

    relay_1.value(0)
    relay_2.value(0)
    relay_3.value(0)
    relay_4.value(0)
    last_motor_ground_time = time.ticks_ms()


def open_gate():
    now = time.ticks_ms()

    print("--- Opening gate ---")

    if time.ticks_diff(now, last_motor_ground_time) > GROUND_DURATION:
        # TODO: test output with a multimeter before connecting to motor!
        relay_1.value(1)
        relay_2.value(0)
        relay_3.value(1)
        relay_4.value(0)


def close_gate():
    now = time.ticks_ms()

    print("--- Closing gate ---")

    if time.ticks_diff(now, last_motor_ground_time) > GROUND_DURATION:
        # TODO: test output with a multimeter before connecting to motor!
        relay_1.value(0)
        relay_2.value(1)
        relay_3.value(0)
        relay_4.value(1)
