from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
from pynput.keyboard import Listener as KeyListener
from pynput.mouse import Listener as MouseListener
from random import randint
import json

# TODO: Currently only working for some specific keys on my keyboard (after the row_col has been mapped)
# TODO: I think it may be in `apply_frame` for `marge_frames`

# =============================================================================
# Classes
# =============================================================================


class Effect:
    frame = None
    func = None
    on_press = None
    on_release = None
    frameCount = None
    effect_options = None

    def __init__(self, zone=None, options=None, func=None, on_press=None, on_release=None):
        self.func = func
        self.on_press = on_press
        self.on_release = on_release
        self.set_size_from_zone(zone)
        self.set_options(options)
        self.frameCount = 0

    def __next__(self):
        if self.func:
            self.func(self)
        self.frameCount += 1

    def clear(self):
        for row in range(len(self.frame)):
            for col in range(len(self.frame[row])):
                self.frame[row][col] = None

    def set_size_from_zone(self, zone):
        if zone is None:
            self.frame = [[]]
            return

        self.frame = []
        for row in get_zone_matrix_map(zone):
            self.frame.append([None] * len(row))

    def set_options(self, options):
        if options is None:
            options = {}
        self.effect_options = options


class EffectZone:
    zone = None
    device_type = None
    effects = None
    input_listener = None
    key_name_to_matrix_map = None

    def __init__(self, zone, device_type, effects=None):
        self.zone = zone
        self.device_type = device_type
        self.set_effects(effects)
        self.key_name_to_matrix_map = {}

    def step_effects(self):
        for e in self.effects:
            next(e)
        self.update()

    def update(self):
        frame = None
        for e in self.effects:
            frame = self.merge_frames(frame, e.frame)
        self.apply_frame(frame)

    def apply_frame(self, frame):
        # Create and apply zone colors
        colors = self.zone.colors
        matrix_map = get_zone_matrix_map(self.zone)
        for row in range(len(frame)):
            if len(matrix_map) < row:
                continue

            for col in range(len(frame[row])):
                if len(matrix_map[row]) < col:
                    continue

                if frame[row][col] is not None and matrix_map[row][col] is not None:
                    colors[matrix_map[row][col]] = frame[row][col]

        self.zone.set_colors(colors)

    def set_effects(self, effects=None):
        if effects:
            self.effects = effects
        else:
            self.effects = []

    def on_press(self, key):
        # Get key position in matrix
        led_row, led_col = self.get_pynput_key_zone_matrix_pos(key)

        if not (led_row and led_col):
            return

        # Run effects
        updated = False
        for e in self.effects:
            if e.on_press:
                e.on_press(e, led_row, led_col)
                updated = True

        if updated:
            self.update()

    def on_release(self, key):
        # Get key position in matrix
        led_row, led_col = self.get_pynput_key_zone_matrix_pos(key)
        if not (led_row and led_col):
            return

        # Run effects
        updated = False
        for e in self.effects:
            if e.on_release:
                e.on_release(e, led_row, led_col)
                updated = True

        if updated:
            self.update()

    def stop_listener(self):
        if self.input_listener:
            self.input_listener.stop()

    def refresh_listener(self):
        # Stop previous listener
        self.stop_listener()

        # Get required listener type
        dev_listener = None
        if self.device_type == DeviceType.KEYBOARD:
            dev_listener = KeyListener
        if self.device_type == DeviceType.MOUSE:
            dev_listener = MouseListener
        if not dev_listener:
            return

        # Get required listener functions
        func_on_press = None
        func_on_release = None
        for e in self.effects:
            if e.on_press:
                func_on_press = self.on_press
            if e.on_release:
                func_on_release = self.on_release

            if func_on_press and func_on_release:
                break
        if not (func_on_press or func_on_release):
            return

        # Start new listener
        self.input_listener = dev_listener(
            on_press=func_on_press,
            on_release=func_on_release
        )
        self.input_listener.start()

    @staticmethod
    def merge_frames(bottom_frame, top_frame):
        if not bottom_frame:
            return top_frame

        for row in range(len(bottom_frame)):
            if len(top_frame) < row:
                continue

            for col in range(len(bottom_frame[row])):
                if len(top_frame[row]) < col:
                    continue

                if top_frame[row][col] is not None:
                    bottom_frame[row][col] = top_frame[row][col]

        return bottom_frame

    def get_pynput_key_zone_matrix_pos(self, key):
        # TODO: Could we save this map with pickle when it changes? then load it on start?
        # TODO: We get funny key values for ctrl+key. Could we just ket each key pressed? or will we have to map it?
        # Get string of key
        key_str = str(key).replace("Key.", "").lower()
        if key_str != "'''":
            key_str = key_str.replace("'", "")
        else:
            key_str = "'"

        # Return if already in the dictionary
        if key_str in self.key_name_to_matrix_map:
            print("Key found:", key_str, self.key_name_to_matrix_map[key_str])
            return self.key_name_to_matrix_map[key_str]

        # Get common_led_names dict TODO: Do this once globally and store it?
        with open("common_led_names.json") as json_file:
            common_led_names = json.load(json_file)

        # Get all possible names for this key
        possible_key_names = [key_str]
        if key_str in common_led_names:
            possible_key_names += common_led_names[key_str]

        # Try to find a possible key name matching an existing LED name
        for possible_key_name in possible_key_names:
            for led in range(len(self.zone.leds)):
                if possible_key_name == self.zone.leds[led].name.replace("Key: ", "").lower():
                    # Get the row and col in the matrix map that refers to that LED
                    matrix_map = get_zone_matrix_map(self.zone)
                    for row in range(len(matrix_map)):
                        for col in range(len(matrix_map[row])):
                            if matrix_map[row][col] == self.zone.leds[led].id:
                                rol_col = (row, col)
                                self.key_name_to_matrix_map[key_str] = rol_col
                                print("Key added:", key_str, rol_col)
                                return rol_col

        # If no matches are found, save it as none as to not search for it next time
        print("Key not found:", key_str)
        self.key_name_to_matrix_map[key_str] = (None, None)
        return None, None

# =============================================================================
# Functions
# =============================================================================


def get_client():
    while True:
        try:
            return OpenRGBClient()
        except ConnectionRefusedError:
            return None


def get_device_by_name(client, name):
    for d in client.ee_devices:
        if d.name == name:
            return d

    for d in client.devices:
        if d.name == name:
            return d


def get_zone_by_name(device, name):
    for z in device.zones:
        if z.name == name:
            return z


def get_zone_matrix_map(zone):
    matrix_map = zone.matrix_map
    if not matrix_map == [[]]:
        return matrix_map

    # If there is no matrix map make a linear one
    return [list(range(len(zone.colors)))]


def get_random_color():
    return RGBColor(randint(0, 255), randint(0, 255), randint(0, 255))


def print_rgb_zone(device, indent=0):
    print(indent*" " + str(device.id) + ". " + device.name)


def print_devices(client):
    device_types = {"ee_devices": client.ee_devices,
                    "devices": client.devices}

    for device_type in device_types:
        print(device_type)
        for device in device_types[device_type]:
            print_rgb_zone(device, 4)
            for zone in device.zones:
                print_rgb_zone(zone, 8)


def print_load_from_json_error(key, device_zone):
    if key in device_zone:
        print("The '" + str(key) + "' from the following json object was not found by openRBG:")
    else:
        print("'" + str(key) + "' does not exist in the following json object:")
    print(device_zone)
    print()
    

def load_effects_from_json(client):
    # Get data from file
    with open("effects.json") as json_file:
        json_data = json.load(json_file)

    # Create list of `EffectZone`s
    effect_zone_list = []
    for device_zone in json_data:
        if not (device := get_device_by_name(client, device_zone["device"])):
            print_load_from_json_error("device", device_zone)
            continue
        if not (zone := get_zone_by_name(device, device_zone["zone"])):
            print_load_from_json_error("zone", device_zone)
            continue
        if not (effects_data := device_zone["effects"]):
            print_load_from_json_error("effects", device_zone)
            continue

        effects = []
        for effect_data in effects_data:
            if not (effect := get_effect_by_name(effect_data["name"])):
                continue
            effect.set_size_from_zone(zone)
            effect.zone = zone
            effect.set_options(effect_data["options"])
            effects.append(effect)
        effect_zone_list.append(EffectZone(zone, device.type, effects))

    return effect_zone_list

# =============================================================================
# Map Effects To JSON Function
# =============================================================================


def get_effect_by_name(effect_name):
    name = effect_name.lower()

    if name == "off":
        return Effect(func=effect_func_apply_black)
    if name == "random colors":
        return Effect(func=effect_func_random_colors)
    if name == "iterate rows with random colors":
        return Effect(func=effect_func_iterate_row_random_color)
    if name == "iterate columns with random colors":
        return Effect(func=effect_func_iterate_col_random_color)
    if name == "toggle random color on press":
        return Effect(on_press=effect_press_toggle_random_color)

# =============================================================================
# Effect Functions
# =============================================================================


def effect_func_random_colors(this_effect: Effect):
    for row in range(len(this_effect.frame)):
        for col in range(len(this_effect.frame[row])):
            this_effect.frame[row][col] = get_random_color()


def effect_func_iterate_row_random_color(this_effect: Effect):
    this_effect.clear()
    row = this_effect.frameCount % len(this_effect.frame)
    color = get_random_color()
    for col in range(len(this_effect.frame[row])):
        this_effect.frame[row][col] = color


def effect_func_iterate_col_random_color(this_effect: Effect):
    this_effect.clear()
    color = get_random_color()

    for row in range(len(this_effect.frame)):
        col = this_effect.frameCount % len(this_effect.frame[row])
        this_effect.frame[row][col] = color


def effect_func_apply_black(this_effect: Effect):
    for row in range(len(this_effect.frame)):
        for col in range(len(this_effect.frame[row])):
            this_effect.frame[row][col] = RGBColor(0, 0, 0)


def effect_press_toggle_random_color(this_effect: Effect, row: int, col: int):
    if this_effect.frame[row][col] is None:
        this_effect.frame[row][col] = get_random_color()
    else:
        this_effect.frame[row][col] = None
