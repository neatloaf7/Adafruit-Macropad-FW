import board
import keypad
import neopixel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import json
from keycodes import profiles
import adafruit_imageload
import displayio
import rotaryio
import digitalio
import time
import random

encoder = rotaryio.IncrementalEncoder(board.ROTB, board.ROTA)
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)

update_interval = 1

display = board.DISPLAY
display.auto_refresh = False

splash = displayio.Group()
numGroup = displayio.Group()


spritebmp = displayio.OnDiskBitmap("sprite.bmp")



sprite = displayio.TileGrid(spritebmp, pixel_shader=spritebmp.pixel_shader,
                                width = 28,
                                height = 2,
                                tile_width=128,
                                tile_height=64,
                                default_tile=0)

lookup  = [list(range(0,6))  , list(range(28,34))]
flicker = [list(range(6,14)) , list(range(34, 42))]
star    = [list(range(14,22)), list(range(42, 50))]
comet   = [list(range(22,28)), list(range(50, 56))]
mixups = [flicker,star,comet]

splash.append(sprite)
display.root_group = splash
display.refresh()
Counter = 0
loopCounter = 0
sceneCounter = 0
scene = 0
loops = 2


KEY_PINS = (
    board.KEY1,
    board.KEY2,
    board.KEY3,
    board.KEY4,
    board.KEY5,
    board.KEY6,
    board.KEY7,
    board.KEY8,
    board.KEY9,
    board.KEY10,
    board.KEY11,
    board.KEY12,
)

profileCurrent = 0
KEYCODES = profiles[profileCurrent]
print("profiles:", len(profiles))

ON_COLOR = (0, 0, 255)
OFF_COLOR = (0, 20, 0) 

keys = keypad.Keys(KEY_PINS, value_when_pressed=False, pull=True)
neopixels = neopixel.NeoPixel(board.NEOPIXEL, 12, brightness=0.4)
neopixels.fill(OFF_COLOR) 
kbd = Keyboard(usb_hid.devices)
last_position = 0
last_update_time = 0



while True:
    event = keys.events.get()
    if event:
        key_number = event.key_number
        # A key transition occurred.
        if event.pressed:
            kbd.press(*KEYCODES[key_number])
            neopixels[key_number] = ON_COLOR

        if event.released:
            kbd.release(*KEYCODES[key_number])
            neopixels[key_number] = OFF_COLOR

    current_position = encoder.position


    #clockwise
    if encoder.position > last_position:
        if profileCurrent < (len(profiles)-1):
            profileCurrent += 1
        else:
            profileCurrent = 0
        
        last_position = current_position
        KEYCODES = profiles[profileCurrent]
        sprite[0] = lookup[profileCurrent][Counter]
        display.refresh()
        
        

    #counterclockwise
    if encoder.position < last_position:
        if profileCurrent > 0:
            profileCurrent -= 1
        else:
            profileCurrent = (len(profiles)-1)
        
        last_position = current_position
        KEYCODES = profiles[profileCurrent]
        sprite[0] = lookup[profileCurrent][Counter]
        display.refresh()
        

    #Display animations
    
    current_time = time.monotonic()
    if current_time - last_update_time >= update_interval:
        if (loopCounter < loops) and (Counter < 5):
            #default 6 frame loop
                Counter += 1
                sprite[0] = lookup[profileCurrent][Counter]
                last_update_time = current_time
                print(current_time)
                display.refresh()
                
        elif loopCounter < loops:
                Counter = 0
                loopCounter += 1
                sprite[0] = lookup[profileCurrent][Counter]
                last_update_time = current_time
                print(current_time)
                display.refresh()
                
        
        else:
            print(len(mixups[scene][0]))
            update_interval = update_interval/8
            if sceneCounter < len(mixups[scene][0]):
                sprite[0] = mixups[scene][profileCurrent][sceneCounter]
                display.refresh()
                sceneCounter += 1
                last_update_time = current_time
                print(current_time)
                display.refresh()
            else:
                Counter += 1
                sprite[0] = lookup[profileCurrent][Counter]
                sceneCounter = 0
                loopCounter = 0
                last_update_time = current_time
                print(current_time)
                display.refresh()
                update_interval = 1

        

       
