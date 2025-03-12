from adafruit_macropad import MacroPad
import board
import keypad
import neopixel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.keycode import Keycode
import displayio
import rotaryio
import digitalio
import time
from adafruit_seesaw.seesaw import Seesaw
from micropython import const
import adafruit_imageload
import json
import busio
import asyncio
import math

#macropad setup
macropad = MacroPad()
macropad.display.auto_refresh = False
macropad.pixels.brightness=0.5
profile = 0

#Import images
backBmp, palette = adafruit_imageload.load("back.bmp", 
                                            bitmap = displayio.Bitmap,
                                            palette = displayio.Palette)
screenBmp, palette = adafruit_imageload.load("screen.bmp", 
                                            bitmap = displayio.Bitmap,
                                            palette = displayio.Palette)
loop = [list(range(0,6)), list(range(6,12))]
wavesBmp, palette = adafruit_imageload.load("waves.bmp", 
                                            bitmap = displayio.Bitmap,
                                            palette = displayio.Palette)
flickerBmp, palette = adafruit_imageload.load("flicker.bmp", 
                                            bitmap = displayio.Bitmap,
                                            palette = displayio.Palette)
flicker = [list(range(0,8)), list(range(8,16))]
star1Bmp, palette = adafruit_imageload.load("star1.bmp", 
                                            bitmap = displayio.Bitmap,
                                            palette = displayio.Palette)
star2Bmp, palette = adafruit_imageload.load("star2.bmp", 
                                            bitmap = displayio.Bitmap,
                                            palette = displayio.Palette)

splash = displayio.Group() #Main group
backGroup = displayio.Group()
screenGroup = displayio.Group(x=11, y=11)
wavesGroup = displayio.Group(x=81, y=0)
flickerGroup = displayio.Group(x=11, y=11)
star1Group     = displayio.Group(x=81, y=0)
star2Group     = displayio.Group(x=81, y=0)

backGrid = displayio.TileGrid(backBmp, pixel_shader=palette)
backGroup.append(backGrid)
screenGrid = displayio.TileGrid(screenBmp, pixel_shader=palette,
                                width=1, height=1,
                                tile_width = 39, tile_height = 26)
screenGroup.append(screenGrid)
wavesGrid = displayio.TileGrid(wavesBmp, pixel_shader=palette,
                                width=1, height=1,
                                tile_width = 47, tile_height = 35)
wavesGroup.append(wavesGrid)
flickerGrid = displayio.TileGrid(flickerBmp, pixel_shader=palette,
                                width=1, height=1,
                                tile_width = 39, tile_height = 26)
flickerGroup.append(flickerGrid)
star1Grid = displayio.TileGrid(star1Bmp, pixel_shader=palette,
                                width=1, height=1,
                                tile_width = 47, tile_height = 35)
star1Group.append(star1Grid)
star2Grid = displayio.TileGrid(star2Bmp, pixel_shader=palette,
                                width=1, height=1,
                                tile_width = 47, tile_height = 35)
star2Group.append(star2Grid)

splash.append(backGroup)
splash.append(screenGroup)
splash.append(wavesGroup)
macropad.display.root_group = splash
macropad.display.refresh()

#Keysetup
with open("config.json", "r") as file:
    config = json.load(file)

keycodes = config["keycodes"]
colors   = config["colors"]
rgb     = config["rgb"]
macropad.pixels[0:12] = [colors[key] for key in rgb[0]]

#gamepadsetup
BUTTON_X = 6
BUTTON_Y = 2
BUTTON_A = 5
BUTTON_B = 1
BUTTON_SELECT = 0
BUTTON_START = 16
button_mask = (
    (1 << BUTTON_X)
    | (1 << BUTTON_Y)
    | (1 << BUTTON_A)
    | (1 << BUTTON_B)
    | (1 << BUTTON_SELECT)
    | (1 << BUTTON_START)
)

i2c_bus = busio.I2C(board.SCL, board.SDA, frequency = 400000)
seesaw = Seesaw(i2c_bus, addr=0x50)
seesaw.pin_mode_bulk(button_mask, seesaw.INPUT_PULLUP)
#Setup analog stick mouse controls
deadzone = 37
mouse = Mouse(usb_hid.devices)
#Initial joystick values (0-1023)
last_x = 511
last_y = 511

altScale = False

actionLast =  time.monotonic()

isSleep    = False
needsWake  = False
timeout    = 30

async def analog():
    global altScale, actionLast
    while True:
        x = 511 - seesaw.analog_read(14, delay=0)
        y = 511 - seesaw.analog_read(15, delay=0)

        if (abs(x) > deadzone) or (abs(y) > deadzone):
            if altScale:
                mouse.move(round(math.copysign((abs(x)-deadzone)/15, x)), -round(math.copysign((abs(y)-deadzone)/15, y)))
            else:
                mouse.move(round(math.copysign((abs(x)-deadzone)/125, x)), -round(math.copysign((abs(y)-deadzone)/125, y)))
            actionLast = time.monotonic()
            
        await asyncio.sleep(0)

async def button():
    xCheck = False
    mouseLeft = False
    mouseRight = False
    global altScale
    while True:
        buttons = seesaw.digital_read_bulk(button_mask, delay=0)

        if not buttons & (1 << BUTTON_X):
            if not xCheck:
                xCheck = True
                altScale = not altScale
        if buttons & (1 << BUTTON_X):
            xCheck = False
        
        if not buttons & (1 << BUTTON_Y):
            mouseLeft = True
        if mouseLeft:
            mouse.press(Mouse.LEFT_BUTTON)
        else:
            mouse.release(Mouse.LEFT_BUTTON)
        mouseLeft = False
        
        if not buttons & (1 << BUTTON_A):
            mouseRight = True
        if mouseRight:
            mouse.press(Mouse.RIGHT_BUTTON)
        else:
            mouse.release(Mouse.RIGHT_BUTTON)
        mouseRight = False
        actionLast = time.monotonic()

        await asyncio.sleep(0.05)

async def key():
    global actionLast
    while True:
        key_event = macropad.keys.events.get()

        if key_event:
            if key_event.pressed == True:
                macropad.keyboard.press(*eval((keycodes[profile][key_event.key_number])))
            else:
                macropad.keyboard.release(*eval((keycodes[profile][key_event.key_number])))
            actionLast = time.monotonic()

        await asyncio.sleep(0)

async def encoder():
    global profile, actionLast, loopTable
    lastPosition = 0
    while True:
        currentPosition = macropad.encoder
        if currentPosition != lastPosition:
            profile = 1 - profile
            lastPosition = currentPosition
            actionLast = time.monotonic()
            screenGrid[0] = loopTable[profile][loopFrame]
            macropad.display.refresh()
        await asyncio.sleep(0)

async def rgbUpdate():
    global needsWake
    lastProfile = profile
    rgbInterval = 0.05
    while True:
        if profile != lastProfile or needsWake:
            lastProfile = profile
            for i in range(0,4):
                ind = slice(i*3, i*3+3)
                macropad.pixels[ind] = [colors["yellow"], colors["yellow"], colors["yellow"]]
                await asyncio.sleep(rgbInterval)
                macropad.pixels[ind] = [colors[key] for key in rgb[profile][ind]]
                await asyncio.sleep(rgbInterval)
        needsWake = False
        await asyncio.sleep(0)

async def sleep():
    global needsWake, isSleep
    while True:
        now = time.monotonic()
        if now - actionLast >= timeout:
            macropad.pixels.fill((0,0,0))
            isSleep = True
            macropad.display_sleep = True
        if isSleep == True and now - actionLast < timeout:
            isSleep = False
            needsWake = True
            macropad.display_sleep = False
        await asyncio.sleep(0)

async def animation():
    updateInterval = 1
    global loopFrame
    global loopTable
    loopFrame = 0
    loopCount      = 0
    maxLoops       = 2
    mixupCount     = 0
    loopTable      = [list(range(0,6)) , list(range(6,12))]
    flickerTable   = [list(range(0,8)), list(range(8,16))]
    while True:
        screenGrid[0] = loopTable[profile][loopFrame]
        wavesGrid[0]  = loopFrame
        macropad.display.refresh()
        await(asyncio.sleep(updateInterval))
        if loopFrame < 5:
            loopFrame += 1
        elif loopCount < maxLoops: 
            loopFrame = 0
            loopCount += 1
        else:
            if mixupCount == 0: 
                splash.remove(screenGroup)
                splash.append(flickerGroup)
                for i in range(8):
                    flickerGrid[0] = flickerTable[profile][i]
                    macropad.display.refresh()
                    await asyncio.sleep(.125)
                splash.remove(flickerGroup)
                splash.append(screenGroup)
                mixupCount = 1
            elif mixupCount == 1:
                splash.remove(wavesGroup)
                splash.append(star1Group)
                loopFrame = 0
                screenGrid[0] = loopTable[profile][loopFrame]
                for i in range(8):
                    star1Grid[0] = i
                    macropad.display.refresh()
                    await asyncio.sleep(.125)
                splash.remove(star1Group)
                splash.append(wavesGroup)
                mixupCount = 2
            elif mixupCount == 2:
                splash.remove(wavesGroup)
                splash.append(star2Group)
                loopFrame = 0
                screenGrid[0] = loopTable[profile][loopFrame]
                for i in range(8):
                    star2Grid[0] = i
                    macropad.display.refresh()
                    await asyncio.sleep(.125)
                splash.remove(star2Group)
                splash.append(wavesGroup)
                mixupCount = 0   
            loopFrame = 1
            loopCount = 0
        await(asyncio.sleep(0))
            


async def main():
    analogTask  = asyncio.create_task(analog())
    buttonTask  = asyncio.create_task(button())
    keyTask     = asyncio.create_task(key())
    encoderTask = asyncio.create_task(encoder())
    rgbTask     = asyncio.create_task(rgbUpdate())
    sleepTask   = asyncio.create_task(sleep())
    animTask    = asyncio.create_task(animation())
    await asyncio.gather(buttonTask)
    await asyncio.gather(analogTask)
    await asyncio.gather(keyTask)
    await asyncio.gather(encoderTask)
    await asyncio.gather(rgbTask)
    await asyncio.gather(sleepTask)

asyncio.run(main())