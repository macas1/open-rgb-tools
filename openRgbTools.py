from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
from random import randint
from time import sleep
import json

# =============================================================================
# Classes
# =============================================================================


class Effect:
    frame = None
    func = None
    isPaused = None
    frameCount = None
    effect_options = None

    def __init__(self, func=None, zone=None, options=None):
        self.func = func
        self.isPaused = False
        self.frameCount = 0
        self.set_size_from_zone(zone)
        self.set_options(options)

    def __next__(self):
        if not self.isPaused:
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

    def apply_to_zone(self, zone):
        colors = zone.colors
        matrix_map = get_zone_matrix_map(zone)

        for row in range(len(self.frame)):
            if len(matrix_map) < row:
                continue

            for col in range(len(self.frame[row])):
                if len(matrix_map[row]) < col:
                    continue

                if self.frame[row][col] is not None and matrix_map[row][col] is not None:
                    colors[matrix_map[row][col]] = self.frame[row][col]
        zone.set_colors(colors)


class EffectZone:
    zone = None
    effects = None

    def __init__(self, zone, effects=None):
        self.zone = zone
        if effects:
            self.effects = effects
        else:
            self.effects = []

    def __next__(self):
        for e in self.effects:
            next(e)
            e.apply_to_zone(self.zone)

    def add_effect_from_func(self, func, match_zone_size=True):
        zone = None
        if match_zone_size:
            zone = self.zone
        self.effects.append(Effect(func, zone))

    def add_effect(self, effect):
        self.effects.append(effect)

# =============================================================================
# Functions
# =============================================================================


def get_client():
    while True:
        try:
            return OpenRGBClient()
        except ConnectionRefusedError:
            sleep(2)


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


def load_effects_from_json(client):
    # Get data from file
    with open("effects.json") as json_file:
        json_data = json.load(json_file)

    # Create list of `EffectZone`s
    effect_zone_list = []
    for device_zone in json_data:
        device = get_device_by_name(client, device_zone["device"])
        zone = get_zone_by_name(device, device_zone["zone"])
        effects_data = device_zone["effects"]

        effects = []
        for effect_data in effects_data:
            effect = get_effect_by_name(effect_data["name"])
            effect.set_size_from_zone(zone)
            effect.set_options(effect_data["options"])
            effects.append(effect)
        effect_zone_list.append(EffectZone(zone, effects))

    return effect_zone_list

# =============================================================================
# Map Effects To JSON Function
# =============================================================================


def get_effect_by_name(effect_name):
    name = effect_name.lower()

    if name == "random colors":
        return Effect(func=effect_func_random_colors)

    if name == "iterate rows with random colors":
        return Effect(func=effect_func_iterate_row_random_color)

    if name == "iterate columns with random colors":
        return Effect(func=effect_func_iterate_col_random_color)

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
