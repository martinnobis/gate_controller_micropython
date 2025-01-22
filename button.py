import time

import machine


DEBOUNCE_DELAY = 40  # milliseconds


class Button(machine.Pin):
    def __init__(self, pin: int, internal_resistor=None):
        self.pressed = False
        self.released = False
        self.last_debounce_time = 0
        self.last_button_state = 1
        self.stable_state = 1
        if internal_resistor:
            super().__init__(pin, machine.Pin.IN, internal_resistor)

    def update(self):
        current_state = self.value()
        now = time.ticks_ms()
        self.released = False

        if current_state != self.last_button_state:
            self.last_debounce_time = now  # Reset debounce timer

        if time.ticks_diff(now, self.last_debounce_time) > DEBOUNCE_DELAY:
            if current_state != self.stable_state:
                self.stable_state = current_state
                if current_state == 1:
                    self.released = True

        self.last_button_state = current_state
