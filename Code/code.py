#import libraries

import board
import keypad
import neopixel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from keycodes import profiles
import displayio
import rotaryio
import digitalio
import time
import random

#Keyboard and rgb setup
keyPins = (
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

keys = keypad.Keys(keyPins, value_when_pressed=False, pull=True)
neopixels = neopixel.NeoPixel(board.NEOPIXEL, 12, brightness=0.4)
downColor = (0, 0, 255)
upColor = (0, 20, 0) 
neopixels.fill(downColor) 
kbd = Keyboard(usb_hid.devices)

#Encoder setup
encoder = rotaryio.IncrementalEncoder(board.ROTB, board.ROTA)
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)
encoderLast = 0

#Setup default profile keycodes
profileCurrent  = 0
keycodes = profiles[profileCurrent]

#display setup
display = board.DISPLAY
display.auto_refresh = False
updateInterval = 1 #seconds per frame
_DISPLAY_SLEEP_COMMAND = 0xAE
_DISPLAY_WAKE_COMMAND = 0xAF

#Import sprite sheet and create TileGrid
spritebmp = displayio.OnDiskBitmap("sprite.bmp")
sprite = displayio.TileGrid(spritebmp, pixel_shader=spritebmp.pixel_shader,
                                width = 28,
                                height = 2,
                                tile_width=128,
                                tile_height=64,
                                default_tile=0)

#Create display group 'group,' populate with sprite default tile, and draw to screen
group = displayio.Group()
group.append(sprite)
display.root_group = group
display.refresh()

#Create lookup tables for animations
loop    = [list(range(0,6))  , list(range(30,36))]
flicker = [list(range(6,14)) , list(range(36, 44))]
star    = [list(range(14,22)), list(range(44, 52))]
comet   = [list(range(22,30)), list(range(52, 60))]
mixups  = [flicker,star,comet]

#Animation counters
loopFrame   = 0
loopCounter = 0
sceneFrame  = 0
scene       = 0
maxLoops    = 2
lastRefresh = 0

#display and rgb timeout
timeKey     = 0
timeEncoder = 0
timeout = 10
#Main loop
while True:
    now = time.monotonic()
    #watch for keypresses and act accordingly
    event = keys.events.get()
    if event:
        key_number = event.key_number
        # A key transition occurred.
        if event.pressed:
            kbd.press(*keycodes[key_number])
            neopixels[key_number] = upColor

        if event.released:
            kbd.release(*keycodes[key_number])
            neopixels[key_number] = downColor
            timeKey = now
    #watch encoder position
    encoderCurrent = encoder.position

    #clockwise
    if encoder.position > encoderLast:
        if profileCurrent < (len(profiles)-1):
            profileCurrent += 1
        else:
            profileCurrent = 0
        
        encoderLast = encoderCurrent
        keycodes = profiles[profileCurrent]
        sprite[0] = loop[profileCurrent][loopFrame]
        display.refresh()
        
    #counterclockwise
    if encoder.position < encoderLast:
        if profileCurrent > 0:
            profileCurrent -= 1
        else:
            profileCurrent = (len(profiles)-1)
        
        encoderLast = encoderCurrent
        keycodes = profiles[profileCurrent]
        sprite[0] = loop[profileCurrent][loopFrame]
        display.refresh()

    #Animation Control
    
    if now - lastRefresh >= updateInterval:
        print(loopCounter)
        #regular loop
        if loopFrame < 5:
            loopFrame += 1
            sprite[0] = loop[profileCurrent][loopFrame]
            print(now)
       
        #if not at maxLoops yet, loop to frame 0 and add one to loopCounter
        elif loopCounter < maxLoops:
            loopFrame = 0
            loopCounter +=1
            sprite[0] = loop[profileCurrent][loopFrame]
            print(now)
        
        #if at maxLoops, skip displaying frame 0 and begin scene. change frame rate to be 8 times faster for the scene.
        if loopCounter == maxLoops:
            updateInterval = updateInterval/8
            if sceneFrame < 8:
                sprite[0] = mixups[scene][profileCurrent][sceneFrame]
                sceneFrame += 1
                lastRefresh = now
                print(now)
            else:
                loopFrame = 1
                print(loopFrame)
                sprite[0] = loop[profileCurrent][loopFrame]
                loopCounter = 0
                sceneFrame = 0
                if scene < 2:
                    scene += 1
                else:
                    scene = 0
                    
                lastRefresh = now
                print(now)
                updateInterval = 1
        lastRefresh = now
        display.refresh()