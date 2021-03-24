from openrgb.utils import RGBColor
from random import randint

# =============================================================================
# Classes
# =============================================================================


class Effect:
    frame = None
    func = None
    isPaused = None
    frameCount = None

    def __init__(self, func, zone=None):
        self.func = func
        self.isPaused = False
        self.frameCount = 0

        if zone is None:
            zone = [[]]
        self.set_size_from_zone(zone)

    def __next__(self):
        if not self.isPaused:
            self.func(self)
            self.frameCount += 1

    def clear(self):
        for row in range(len(self.frame)):
            for col in range(len(self.frame[row])):
                self.frame[row][col] = None

    def set_size_from_zone(self, zone):
        self.frame = []
        for row in zone.matrix_map:
            self.frame.append([None] * len(row))

    def apply_to_zone(self, zone):
        colors = zone.colors
        matrix_map = zone.matrix_map

        for row in range(len(self.frame)):
            if len(matrix_map) < row:
                continue

            for col in range(len(matrix_map[row])):
                if len(matrix_map[row]) < col:
                    continue

                if self.frame[row][col] is not None:
                    colors[matrix_map[row][col]] = self.frame[row][col]
        zone.set_colors(colors)


class EffectZone:
    zone = None
    effects = None

    def __init__(self, zone, effects = []):
        self.zone = zone
        self.effects = effects

    def __next__(self):
        for e in self.effects:
            next(e)
            e.apply_to_zone(self.zone)

    def add_effect_from_func(self, func, match_zone_size=True):
        zone = None
        if match_zone_size:
            zone = self.zone
        self.effects.append(Effect(func, zone))

    def add_effect(self, effect, match_zone_size=True):
        self.effects.append(effect)

# =============================================================================
# Functions
# =============================================================================


def get_device_by_name(client, name):
    for d in client.ee_devices:
        if d.name == name:
            return d

    for d in client.devices:
        if d.name == name:
            return d


def get_random_color():
    return RGBColor(randint(0, 255), randint(0, 255), randint(0, 255))


def print_names(obj_arr):
    for i in range(len(obj_arr)):
        print("(" + str(i) + ") " + obj_arr[i].name)


def print_devices(client):
    print("ee_devices")
    print_names(client.ee_devices)

    print("devices")
    print_names(client.devices)
