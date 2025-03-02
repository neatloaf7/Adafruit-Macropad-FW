# Adafruit-Macropad-FW
## My CircuitPython firmware used on the Adafruit Macropad
![gamesloop](https://github.com/user-attachments/assets/197278c6-db11-4f7f-87a4-4d8d55d6752c)

I ported over my settings from QMK as the CircuitPython displayio library makes animations simpler to work with.
Not having to compile firmware is a big advantage, but my way of emulating QMK keymaps is not as easy to use.
If you don't need as much control over the display, the [Adafruit_CircuitPython_MacroPad](https://github.com/adafruit/Adafruit_CircuitPython_MacroPad) library is a good place to start creating your own firmware.

Uses the [Adafruit_HID](https://github.com/adafruit/Adafruit_CircuitPython_HID) and [neopixel](https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel) libraries.
### Features
- Supports multiple profiles, currently using 2
- profile keymaps and neopixel colors are set in keycodes.py and rgbs.py
- Looping animation that indicates currently selected profile
  - After a set number of loops, play a fast effect animation
- OLED and neopixel timeout

### Issues
- clean up serial messages
- add encoder debouncer
