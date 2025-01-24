import time

import machine

#
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
# 4-channel 5V relay board has a LOW level trigger!!!!
# https://www.handsontec.com/dataspecs/4Ch-relay.pdf
#

GROUND_DURATION = 0.1  # s
COAST_DURATION = 1  # s

last_motor_ground_time = 0

RELAY_1_PIN = 19
RELAY_2_PIN = 20
RELAY_3_PIN = 21
RELAY_4_PIN = 22

relay_1 = machine.Pin(RELAY_1_PIN, machine.Pin.OUT)
relay_2 = machine.Pin(RELAY_2_PIN, machine.Pin.OUT)
relay_3 = machine.Pin(RELAY_3_PIN, machine.Pin.OUT)
relay_4 = machine.Pin(RELAY_4_PIN, machine.Pin.OUT)


def _coast_motor():
    """
    Coast the motor by just opening the top relays. Keeping one of the bottom relays closed.
    """
    print(f"Motor: Coasting for {COAST_DURATION}s")
    relay_1.value(1)  # open
    relay_2.value(1)  # open
    time.sleep(COAST_DURATION)


def _ground_motor():
    """
    Ground the motor by resetting the outputs, by default the motor is grounded.
    """
    relay_1.value(1)  # open
    relay_2.value(1)  # open

    time.sleep(0.2)

    relay_3.value(1)  # close
    relay_4.value(1)  # close
    time.sleep(GROUND_DURATION)


def stop():
    """
    Stop the motor.

    Blocking sleep after coasting as we aren't interested in
    responding to inputs so quickly when the motor is changing
    direction.
    """
    _coast_motor()
    _ground_motor()


def open_gate():
    # open bottom relays first to prevent short
    relay_3.value(0)  # open
    relay_4.value(1)  # close

    time.sleep(0.2)

    relay_1.value(0)  # close
    relay_2.value(1)  # open


def close_gate():
    # open bottom relays first to prevent short
    relay_3.value(1)  # close
    relay_4.value(0)  # open

    time.sleep(0.2)

    relay_1.value(1)  # open
    relay_2.value(0)  # close
