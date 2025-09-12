# Adafruit-Macropad-FW
## My CircuitPython firmware used on the Adafruit Macropad
![gamesloop](https://github.com/user-attachments/assets/197278c6-db11-4f7f-87a4-4d8d55d6752c)

I ported over my settings from QMK as the CircuitPython displayio library makes animations simpler to work with.
Not having to compile firmware is a big advantage, but my way of emulating QMK keymaps is not as easy to use.
See my [hackaday](https://hackaday.io/project/202556-adafruit-macropad-modding) page for more details.

![image](https://github.com/user-attachments/assets/059e5eff-10fc-4808-ab1d-5e2780d0a23f)

Uses the [Adafruit_CircuitPython_MacroPad](https://github.com/adafruit/Adafruit_CircuitPython_MacroPad) and [adafruit_seesaw](https://github.com/adafruit/Adafruit_Seesaw) libraries.
### Features
- Supports multiple profiles (2 in use)
- profile keymaps and neopixel colors are set in config.json
- OLED animation set by current profile
  - Looping animation that indicates currently selected profile
  - After a set number of loops, play a faster "random effect" animation
- OLED and neopixel timeout
- I2c gamepad added for mouse control

### To do list
- Modify key coroutine logic to recognize and accept consumer control codes if present in config.json keymap
- add more pictures

### Issues
- Animation logic is spaghetti
  
### Updates
- 11SEP25 - Small coroutine optimizations for smoother analog stick mouse control
  - Cleaned some formatting and removed unused libraries
  - Added some comments
  - Removed rgbUpdate task, rgbUpdate is now called by encoder and sleep coroutines when needed
  - Changed sleep coroutine logic and added an event to track wake/sleep status
  - Changed seesaw button coroutine logic to avoid looping through all coroutine checks if button state has not changed
  - Changed animation coroutine logic to check if awake is set before running loop
  - Changed some debounce timing
- 11MAR25
  - changed code to use asyncio, profile configs are now imported with a JSON file.
  - split up sprite bitmap to only update portions of screen that are animated. Image size reduced from 241kb to 13kb, and can now load using adafruit_imageload
  - added [QT Gamepad](https://learn.adafruit.com/gamepad-qt/overview) for emulating a mouse, plugged into the STEMMA port.
- 02MAR25
  - Added an animation for the LEDs that cascades the new rgb profile downwards
