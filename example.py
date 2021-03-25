from openRgpTools import *
from time import sleep

# ===================================================
# Constants
# ===================================================


KEYBOARD_NAME = "Razer BlackWidow Elite"
MOUSE_NAME = "Razer DeathAdder Elite"


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


def e3(this_effect: Effect):
    this_effect.clear()
    color = get_random_color()

    for row in range(len(this_effect.frame)):
        col = this_effect.frameCount % len(this_effect.frame[row])
        this_effect.frame[row][col] = color


# ===================================================
# Main
# ===================================================


def main():
    # Main Loop
    while True:
        # Get Client
        client = get_client()
        print_devices(client)

        # Add keyboard and add effects
        keyboard = EffectZone(get_device_by_name(client, KEYBOARD_NAME).zones[0])
        keyboard.add_effect_from_func(e1)
        keyboard.add_effect_from_func(e2)
        keyboard.add_effect_from_func(e3)

        # Add mouse and effects
        mouse = EffectZone(get_device_by_name(client, MOUSE_NAME).zones[0])
        mouse.add_effect_from_func(e1)

        # Loop through effect frames
        while True:
            try:
                next(keyboard)
                next(mouse)
            except ConnectionAbortedError:
                break
            sleep(1)


if __name__ == "__main__":
    main()
