# Claude Reminder

Small ESP32-C3 reminder utility for sending a physical notification when Claude Code needs attention.

## Contents

- `app.py` - installs missing Python dependencies, flashes the ESP32-C3 firmware, and copies the Claude settings and notification hook.
- `notify.py` - finds the connected ESP32-C3 and sends the trigger byte over serial.
- `ESP.ino` - Arduino sketch that drives the solenoid on GPIO 4.
- `firmware.bin` - prebuilt ESP32-C3 firmware image used by `app.py`.
- `settings.json` - Claude Code hook configuration.

## Requirements

- Python 3
- ESP32-C3 connected over USB
- An available `esptool` installation or permission for `app.py` to install it
- Arduino IDE or Arduino CLI if rebuilding the sketch

## Usage

Run the setup and firmware tool from this directory:

```powershell
python app.py
```

The tool detects the ESP32-C3, flashes `firmware.bin`, saves the detected serial port locally, and copies the Claude hook files into `%USERPROFILE%\\.claude`.

The notification hook can also be run directly:

```powershell
python notify.py
```

## Hardware

The sketch uses GPIO 4 to control the solenoid. Use an appropriate driver circuit and external power supply; do not connect a solenoid directly to an ESP32 GPIO pin.
