import time

import machine

import rgb
import motor
from button import Button


class State:
    AJAR = "Ajar"
    OPENED = "Opened"
    OPENING = "Opening"
    CLOSED = "Closed"
    CLOSING = "Closing"


#
# STATES
#
state = State.AJAR
prev_state = None  # should only either be OPENING OR CLOSING
prev_action = None

#
# BUTTONS
#
boot_button = Button(9, machine.Pin.PULL_UP)
remote_open = machine.Pin(2, machine.Pin.IN)
remote_close = machine.Pin(3, machine.Pin.IN)


def update_inputs():
    """
    Update all inputs for this iteration of the loop.
    """
    global boot_button

    boot_button.update()


def update_outputs():
    global state, prev_state

    if state != prev_state:
        if prev_action in (State.OPENING, State.CLOSING):
            motor.stop()
        elif state == State.OPENING:
            motor.open_gate()
        elif state == State.CLOSING:
            motor.close_gate()


def update_state():
    """
    Update the state (if required) for this iterations of the loop.
    """
    global state, prev_state, prev_action, boot_button

    prev_state = state

    if state == State.AJAR:
        rgb.flash(0.5, rgb.YELLOW)
        if boot_button.released:
            if prev_action == State.CLOSING:
                state = State.OPENING
            elif prev_action == State.OPENING:
                state = State.CLOSING
            else:
                state = State.CLOSING  # close to be safe
        elif remote_close.value() == 1:
            state = State.CLOSING
        elif remote_open.value() == 1:
            state = State.OPENING
    elif state == State.OPENED:
        rgb.flash(0.5, rgb.GREEN)
        if boot_button.released:
            state = State.CLOSING
        elif remote_close.value() == 1:
            state = State.CLOSING
    elif state == State.CLOSED:
        rgb.flash(0.5, rgb.RED)
        if boot_button.released:
            state = State.OPENING
        elif remote_open.value() == 1:
            state = State.OPENING
    elif state in (State.OPENING, State.CLOSING):
        prev_action = state
        rgb.flash(0.5, rgb.BLUE)
        if boot_button.released:
            state = State.AJAR
        elif remote_close.value() == 1:
            state = State.CLOSING
        elif remote_open.value() == 1:
            state = State.OPENING


def loop():
    global state, prev_state, boot_button

    while True:
        update_inputs()
        update_state()
        update_outputs()
        print(state)

        time.sleep(0.1)


if __name__ == "__main__":
    loop()
