import time
from collections import deque

import machine
import ssd1306

import rgb
import motor
import wifi
from button import Button


OPEN_SENSOR_HIGH_THRESHOLD = 1500  # mV


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
remote_open = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)
remote_close = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)

#
# INPUT PINS
#
gate_closed_sensor = machine.Pin(2, machine.Pin.IN)
gate_opened_sensor = machine.ADC(machine.Pin(3))

# Configure ADC width and attenuation if needed
gate_opened_sensor.width(machine.ADC.WIDTH_12BIT)  # 12-bit width
gate_opened_sensor.atten(machine.ADC.ATTN_6DB)  # 6dB attenuation

#
# DISPLAY
#
# using default address 0x3C
i2c = machine.SoftI2C(sda=machine.Pin(1), scl=machine.Pin(0))
display = ssd1306.SSD1306_I2C(128, 32, i2c)

#
# Wifi
#
wifi2 = wifi.Wifi()


def adc_raw_to_vout(raw):
    """
    Scaled with a multimeter, not the formula given in esp32 docs, so will look slightly different.
    """
    return (raw * 2000) / 4095


def update_outputs():
    global state, prev_state

    if state != prev_state:
        if prev_state in (State.OPENING, State.CLOSING):
            display.text("Motor stopping", 0, 24, 1)
            display.show()
            motor.stop()

        if state == State.OPENING:
            motor.open_gate()
            if prev_state in (State.CLOSED, State.OPENED):
                # pause for 1 second as otherwise the sensor still read either open or close
                time.sleep(2)
        elif state == State.CLOSING:
            motor.close_gate()
            if prev_state in (State.CLOSED, State.OPENED):
                # pause for 1 second as otherwise the sensor still read either open or close
                time.sleep(2)


def update_state():
    """
    Update the state (if required) for this iterations of the loop.
    """
    global state, prev_state, prev_action, boot_button, wifi2, open_sensor_readings

    boot_button.update()

    prev_state = state

    open_sensor_reading = adc_raw_to_vout(gate_opened_sensor.read())
    print(f"open sensor reading: {open_sensor_reading}")

    # regardless of the state, always check whether the gate is closed/opened
    if gate_closed_sensor.value() == 1:
        state = State.CLOSED
    elif open_sensor_reading > OPEN_SENSOR_HIGH_THRESHOLD:
        state = State.OPENED

    wifi_action_request = wifi2.get_gate_action_request()

    if state == State.AJAR:
        rgb.flash(0.5, rgb.YELLOW)
        if boot_button.released:
            if prev_action == State.CLOSING:
                state = State.OPENING
            elif prev_action == State.OPENING:
                state = State.CLOSING
            else:
                state = State.CLOSING  # close to be safe
        elif remote_close.value() == 1 or wifi_action_request == "CLOSE":
            state = State.CLOSING
        elif remote_open.value() == 1 or wifi_action_request == "OPEN":
            state = State.OPENING
    elif state == State.OPENED:
        rgb.flash(0.5, rgb.GREEN)
        if boot_button.released:
            state = State.CLOSING
        elif remote_close.value() == 1 or wifi_action_request == "CLOSE":
            state = State.CLOSING
    elif state == State.CLOSED:
        rgb.flash(0.5, rgb.RED)
        if boot_button.released:
            state = State.OPENING
        elif remote_open.value() == 1 or wifi_action_request == "OPEN":
            state = State.OPENING
    elif state in (State.OPENING, State.CLOSING):
        prev_action = state
        rgb.flash(0.5, rgb.BLUE)
        if boot_button.released:
            state = State.AJAR
        elif remote_close.value() == 1 or wifi_action_request == "CLOSE":
            state = State.CLOSING
        elif remote_open.value() == 1 or wifi_action_request == "OPEN":
            state = State.OPENING
        elif wifi_action_request == "STOP":
            state = State.AJAR


def main():
    global state, prev_state, boot_button

    motor.stop()

    is_wifi_connected = False
    ip_address = None

    print(f"Gate: {state}")

    ap_active, ap_ip_address = wifi2.create_access_point("esp32", "password")

    if ap_active:
        wifi2.start_http_server()
        wifi2.set_gate_state(state)

    # is_wifi_connected, ip_address = wifi.connect("Unifi-A", "UtCW.oMi@dy4vK@ZNMX-wAt4")

    # if is_wifi_connected:
    #     wifi.start_http_server()

    while True:
        display.fill(0)  # clear screen

        update_state()

        if state != prev_state:
            wifi2.set_gate_state(state)
            print("--------------------------")
            print(f"Gate: {state}")

        display.text(f"Gate: {state}", 0, 0, 1)

        if is_wifi_connected:
            display.text(f"WIFI {ip_address}", 0, 12, 1)
        elif ap_active:
            display.text(f"AP {ap_ip_address}", 0, 12, 1)
        else:
            display.text("No WIFI", 0, 12, 1)

        update_outputs()

        display.show()

        time.sleep(0.1)
        # machine.idle()


if __name__ == "__main__":
    main()
