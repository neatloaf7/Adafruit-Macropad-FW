import storage
import board, digitalio
import microcontroller

# On the Macropad, pressing a key grounds it. You need to set a pull-up.
# If not pressed, the key will be at +V (due to the pull-up).
button = digitalio.DigitalInOut(board.KEY12)
button.pull = digitalio.Pull.UP

# Disable devices only if button is not pressed.
if button.value:
   storage.disable_usb_drive()

microcontroller.cpu.frequency = 250000000