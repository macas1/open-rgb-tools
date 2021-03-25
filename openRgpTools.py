from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
from random import randint
from time import sleep

# =============================================================================
# Classes
# =============================================================================


class Effect:
    frame = None
    func = None
    isPaused = None
    frameCount = None

    def __init__(self, func=None, zone=None):
        self.func = func
        self.isPaused = False
        self.frameCount = 0

        if zone is None:
            self.frame = [[]]
        self.set_size_from_zone(zone)

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
        self.frame = []
        for row in get_zone_matrix_map(zone):
            self.frame.append([None] * len(row))

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
