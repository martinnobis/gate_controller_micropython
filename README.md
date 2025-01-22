# esp32

The virtual environmenet has installed:

- esptool
- mpremote

```bash
source venv/bin/activate # activate the venv
```

## Commands

```bash
mpremote connect /dev/tty.usbmodem1101 repl  # run REPL on the device
mpremote connect /dev/tty.usbmodem1101 fs ls  # show files on device
mpremote connect /dev/tty.usbmodem1101 fs cp main.py rgb.py :  # upload the main.py and rgb.py files
mpremote connect /dev/tty.usbmodem1101 reset  # reboot the device
```

## Debugging

```bash
ls /dev/tty.usb*  # to show devices, aliased to lsdev
lsof | grep /dev/tty.usbmodem1101 # to show any running processes using the device
kill <pid>  # kill any running processes using the device
```

## Notes

`threading` is not available in micropython, use `_thread` instead.
