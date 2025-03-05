#import libraries
import board
import keypad
import neopixel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.keycode import Keycode
from keycodes import profiles
from rgbs import colors
import displayio
import rotaryio
import digitalio
import time
from adafruit_seesaw.seesaw import Seesaw
from micropython import const
import adafruit_imageload


#gamepadsetup
BUTTON_X = const(6)
BUTTON_Y = const(2)
BUTTON_A = const(5)
BUTTON_B = const(1)
BUTTON_SELECT = const(0)
BUTTON_START = const(16)
button_mask = const(
    (1 << BUTTON_X)
    | (1 << BUTTON_Y)
    | (1 << BUTTON_A)
    | (1 << BUTTON_B)
    | (1 << BUTTON_SELECT)
    | (1 << BUTTON_START)
)
mouse = Mouse(usb_hid.devices)

i2c_bus = board.STEMMA_I2C()  # The built-in STEMMA QT connector on the microcontroller
# i2c_bus = board.I2C()  # Uses board.SCL and board.SDA. Use with breadboard.

seesaw = Seesaw(i2c_bus, addr=0x50)

seesaw.pin_mode_bulk(button_mask, seesaw.INPUT_PULLUP)

last_x = 511
last_y = 511
deadzone = 37
altScale = False
xCheck = False

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
kbd = Keyboard(usb_hid.devices)

neopixels = neopixel.NeoPixel(board.NEOPIXEL, 12, brightness=0.4)
rgbWait   = .04
updateRow = 0
rgbLast   = 0
rgbChange = True
isBlack   = False

def setPixels(profileCurrent, updateRow):
    global rgbLast
    global rowInd
    colorSet = colors[profileCurrent]
    rowInd = slice(updateRow*3, updateRow*3+3)
    neopixels[rowInd] = colorSet[rowInd]
    rgbLast = time.monotonic()

setPixels(0,0)

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
sleepCmd = 0xAE
wakeCmd = 0xAF
display.bus.send(wakeCmd, b"")

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
timeKey     = time.monotonic()
timeEncoder = time.monotonic()
timeout     = 20 #timeout interval in seconds
isSleep     = False


#Main loop
while True:
    now = time.monotonic()
        
    #watch for keypresses and act accordingly
    event = keys.events.get()
    if event:
        if isSleep is True:
            isSleep = False
            display.bus.send(wakeCmd, b"")
            rgbChange = True

        key_number = event.key_number
        timeKey    = now
        # A key transition occurred.
        if event.pressed:
            kbd.press(*keycodes[key_number])

        if event.released:
            kbd.release(*keycodes[key_number])
            timeKey = now
    #watch encoder position
    encoderCurrent = encoder.position

    #clockwise
    if encoder.position > encoderLast:
        if profileCurrent < (len(profiles)-1):
            profileCurrent += 1
        else:
            profileCurrent = 0
        
        if isSleep is True:
            isSleep = False
            display.bus.send(wakeCmd, b"")
            #setPixels(profileCurrent, updateRow)

        encoderLast = encoderCurrent
        timeEncoder = now
        keycodes = profiles[profileCurrent]
        sprite[0] = loop[profileCurrent][loopFrame]
        display.refresh()
        updateRow = 0
        rgbChange = True
        
    #counterclockwise
    if encoder.position < encoderLast:
        if profileCurrent > 0:
            profileCurrent -= 1
        else:
            profileCurrent = (len(profiles)-1)
        
        if isSleep is True:
            isSleep = False
            display.bus.send(wakeCmd, b"")
            #setPixels(profileCurrent)
        
        encoderLast = encoderCurrent
        timeEncoder = now
        keycodes = profiles[profileCurrent]
        sprite[0] = loop[profileCurrent][loopFrame]
        display.refresh()
        updateRow = 0
        rgbChange = True

    #Animation Control
    if now - lastRefresh >= updateInterval:
        #regular loop
        if loopFrame < 5:
            loopFrame += 1
            sprite[0] = loop[profileCurrent][loopFrame]
       
        #if not at maxLoops yet, loop to frame 0 and add one to loopCounter
        elif loopCounter < maxLoops:
            loopFrame = 0
            loopCounter +=1
            sprite[0] = loop[profileCurrent][loopFrame]
        
        #if at maxLoops, skip displaying frame 0 and begin scene. change frame rate to be 8 times faster for the scene.
        if loopCounter == maxLoops:
            updateInterval = updateInterval/8
            if sceneFrame < 8:
                sprite[0] = mixups[scene][profileCurrent][sceneFrame]
                sceneFrame += 1
                lastRefresh = now
            else:
                loopFrame = 1
                sprite[0] = loop[profileCurrent][loopFrame]
                loopCounter = 0
                sceneFrame = 0
                if scene < 2:
                    scene += 1
                else:
                    scene = 0
                    
                lastRefresh = now
                updateInterval = 1
        lastRefresh = now
        display.refresh()

    #RGB control
    #Cascade profile changes downward
    if now - rgbLast >= rgbWait and rgbChange:
        if updateRow < 3:
            if isBlack:
                neopixels[slice(updateRow*3, updateRow*3+3)] = (50,50,0) *3
                rgbLast = now
                isBlack = False
            else:
                setPixels(profileCurrent, updateRow)
                updateRow += 1
                isBlack = True
    
        else:
            if isBlack:
                neopixels[slice(updateRow*3, updateRow*3+3)] = (50,50,0) *3
                rgbLast = now
                isBlack = False
            else:
                setPixels(profileCurrent, updateRow)
                updateRow = 0
                rgbChange = False
                isBlack = True

    #Gamepad
    x = 511 - seesaw.analog_read(14)
    y = 511 - seesaw.analog_read(15)

    if (abs(x) > deadzone) or (abs(y) > deadzone):
        if altScale:
            mouse.move(round(x/7), -round(y/7))
        else:
            mouse.move(round(x/50), -round(y/50))
        print(x, y)

    buttons = seesaw.digital_read_bulk(button_mask)

    if not buttons & (1 << BUTTON_X):
        if not xCheck:
            xCheck = True
            altScale = not altScale
            print ("altScale:", altScale)
        print("Button x pressed")

    if buttons & (1 << BUTTON_X):
        xCheck = False

    mouseLeft = False
    if not buttons & (1 << BUTTON_Y):
        print("Button y pressed")
        mouseLeft = True

    if mouseLeft:
        mouse.press(Mouse.LEFT_BUTTON)
    else:
        mouse.release(Mouse.LEFT_BUTTON)

    mouseRight = False

    if not buttons & (1 << BUTTON_A):
        print("Button A pressed")
        mouseRight = True

    if mouseRight:
        mouse.press(Mouse.RIGHT_BUTTON)
    else:
        mouse.release(Mouse.RIGHT_BUTTON)

    if not buttons & (1 << BUTTON_B):
        print("Button B pressed")

    if not buttons & (1 << BUTTON_SELECT):
        print("Button Select pressed")

    if not buttons & (1 << BUTTON_START):
        print("Button Start pressed")

    #OLED Sleep
    if (now - max(timeKey, timeEncoder) >= timeout) and isSleep is False:
        isSleep = True
        display.bus.send(sleepCmd, b"")
        neopixels.fill((0,0,0))
