from adafruit_hid.keycode import Keycode
profiles = [
    
    [
    (Keycode.SHIFT, Keycode.F3),     (Keycode.SHIFT, Keycode.F1), (Keycode.SHIFT, Keycode.F2),
    (Keycode.SHIFT, Keycode.ESCAPE), (Keycode.UP_ARROW,) ,        (Keycode.ENTER,),
    (Keycode.LEFT_ARROW,),           (Keycode.DOWN_ARROW,),       (Keycode.RIGHT_ARROW,),
    (Keycode.F13,),                  (Keycode.F14,),              (Keycode.F15,)
    ],

    
    [
    (Keycode.SEVEN,),      (Keycode.EIGHT,), (Keycode.NINE,),
    (Keycode.FOUR,),      (Keycode.FIVE,),  (Keycode.SIX,),
    (Keycode.ONE,),       (Keycode.TWO,),   (Keycode.THREE,),
    (Keycode.BACKSPACE,), (Keycode.ZERO,),  (Keycode.ENTER,)
    ]
]