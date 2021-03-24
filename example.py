from openRgpTools import *
from openrgb import OpenRGBClient
from time import sleep


# ===================================================
# Constants
# ===================================================


KEYBOARD_NAME = "Razer BlackWidow Elite"


# ===================================================
# Effects
# ===================================================


def e1(this_effect: Effect):
    for row in range(len(this_effect.frame)):
        for col in range(len(this_effect.frame[row])):
            this_effect.frame[row][col] = get_random_color()


def e2(this_effect: Effect):
    this_effect.clear()
    row = this_effect.frameCount % len(this_effect.frame)
    color = get_random_color()
    for col in range(len(this_effect.frame[row])):
        this_effect.frame[row][col] = color


# ===================================================
# Main
# ===================================================


def main():
    keyboard = EffectZone(get_device_by_name(OpenRGBClient(), KEYBOARD_NAME).zones[0])

    keyboard.add_effect_from_func(e1)
    keyboard.add_effect_from_func(e2)

    while True:
        next(keyboard)
        sleep(1)


if __name__ == "__main__":
    main()
