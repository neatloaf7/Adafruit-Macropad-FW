# Adafruit-Macropad-FW
## My CircuitPython firmware used on the Adafruit Macropad
### Features
- Supports multiple profiles, currently using 2
- profile keymaps and neopixel colors are set in keycodes.py and rgbs.py
- Looping animation that indicates currently selected profile
  - After a set number of loops, play a fast effect animation
- OLED and neopixel timeout

### Issues
- if asleep, could pause writing new frames to display memory.
- could reformat keycodes.py
- could store profile info in .JSON
- could clean up serial messages
- could clean up encoder code
