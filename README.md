# Adafruit-Macropad-FW
## My CircuitPython firmware used on the Adafruit Macropad
![gamesloop](https://github.com/user-attachments/assets/197278c6-db11-4f7f-87a4-4d8d55d6752c)

I ported over my settings from QMK as the CircuitPython displayio library makes animations simpler to work with.
Not having to compile firmware is a big advantage, but my way of emulating QMK keymaps is not as easy to use.
See my [hackaday](https://hackaday.io/project/202556-adafruit-macropad-modding) page for more details.

![image](https://github.com/user-attachments/assets/059e5eff-10fc-4808-ab1d-5e2780d0a23f)

Uses the [Adafruit_CircuitPython_MacroPad](https://github.com/adafruit/Adafruit_CircuitPython_MacroPad) and [adafruit_seesaw](https://github.com/adafruit/Adafruit_Seesaw) libraries.
### Features
- Supports multiple profiles, currently using 2
- profile keymaps and neopixel colors are set in config.json
- Looping animation that indicates currently selected profile
  - After a set number of loops, play a fast effect animation
- OLED and neopixel timeout
- I2c gamepad added for mouse control

### Issues
- clean up formatting, add comments
- remove vestigial libraries
- add more pictures

### Updates
- 11MAR25
  - changed code to use asyncio, profile configs are now imported with a JSON file.
  - split up sprite bitmap to only update portions of screen that are animated. Image size reduced from 241kb to 13kb, and can now load using adafruit_imageload
  - added [QT Gamepad](https://learn.adafruit.com/gamepad-qt/overview) for emulating a mouse, plugged into the STEMMA port.
- 02MAR25
  - Added an animation for the LEDs that cascades the new rgb profile downwards
