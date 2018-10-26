#! /usr/bin/python3
import helpers.vector as v
import logging
from pynput import keyboard
import curses

logging.basicConfig(filename='app_log.txt', level = logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')

f = open('./app_log.txt', 'w')
f.write('')
f.close()


class Pixel:

    def __init__(self, symbol, x, y, parent_name, print_priority, color):
        self.symbol = symbol
        self.rel_pos = v.Vector(x, y)
        self.empty = self.is_empty()
        self.parent_name = parent_name
        self.abs_pos = v.Vector(0, 0)
        self.print_priority = print_priority
        self.color = color

    def is_empty(self):
        if self.symbol == ' ':
            return True
        else:
            return False

    def __lt__(self, other):
        return self.abs_pos.x < other.abs_pos.x or \
               (self.abs_pos.x == other.abs_pos.x and self.abs_pos.y < other.abs_pos.y)

    def __str__(self):
        return self.symbol + "({}, {})".format(self.abs_pos.x, self.abs_pos.y)


# Represents a unit, made of pixels.
# Is uploaded from a folder as text file
class Unit:

    def __init__(self, path, name, collidable=True, print_priority=0, color=curses.COLOR_WHITE, text=False):
        self.print_priority = print_priority
        self.name = name
        self.collidable = collidable
        self.path = path
        self.color = color
        self.pos = v.Vector(0, 0)
        if not text:
            f = open(path).readlines()
            f = [line[:-1] for line in f]
            self.raw = ''.join(f)
            self.body = self.build_unit(f)
            self.width = v.Vector(max([len(x) for x in f]), 0)
            self.height = v.Vector(0, len(f))

    def build_unit(self, lines):
        pixels = []
        y = 0
        for line in lines[::-1]:
            x = 0
            for pixel in line:
                p = Pixel(pixel, x, y, self.name, self.print_priority, self.color)
                pixels.append(p)
                x += 1
            y += 1
        return pixels

    def copy(self):
        copy = Unit(self.path, self.name, self.collidable, self.print_priority, self.color)
        return copy

    def __str__(self):
        result = ''
        for p in self.body:
            result += str(p)
        return result


class MainUnit(Unit):
    def __init__(self, path, name, collidable=True, print_priority=999, color=curses.A_NORMAL):
        Unit.__init__(self, path, name, collidable, print_priority, color)
        self.def_velocity = v.Vector(0, 0)
        self.collided = False
        self.squated = False
        self.squated_unit = Unit('./units/invadersquat','invader', collidable=True, print_priority=999, color=curses.COLOR_RED)
        self.normal_unit = Unit(self.path, 'invader', collidable=True, print_priority=999, color=curses.COLOR_RED)
        self.jump = []

        self.action_map = {'32': self.init_jump,
                           '258': self.fast_landing,
                           '-1': self.do_nothing}
        self.release_actions = {'258': self.standup,
                                '-1': self.do_nothing}

    @staticmethod
    def do_nothing():
        return -1

    def standup(self):
        # logging.debug('standing up')
        self.body = self.normal_unit.body
        self.squated = False

    def init_jump(self):
        self.make_jump_arr()

    def fast_landing(self):
        if self.is_jumping():
            last = self.jump[-1]
            if last.y < 0:
                self.jump = list(map(lambda x: x - v.Vector(0, 3), self.jump))
        else:
            if not self.squated:
                self.body = self.squated_unit.body
                self.squated = True

    def make_jump_arr(self):
        if self.is_jumping():
            return
        result = []
        for i in range(3):
            for x in range(2):
                result.append(v.Vector(0, -2))
        for s in range(4):
            result.append(v.Vector(0, -1))
        for s in range(4):
            result.append(v.Vector(0, 1))
        for i in range(3):
            for x in range(2):
                result.append(v.Vector(0, 2))

        self.jump = result

    def is_jumping(self):
        return len(self.jump) > 0

    def update_velocity(self):
        if self.is_jumping():
            self.def_velocity = self.jump.pop()

    def clear_jump_arr(self):
        self.jump.clear()


class BackgroundUnit(Unit):

    def __init__(self, path, name, collidable=True, print_priority=0, color=curses.COLOR_WHITE, xpos=500, ypos=0):
        Unit.__init__(self, path, name, collidable, print_priority, color)
        self.pos = v.Vector(xpos, ypos)

    def copy(self):
        copy = BackgroundUnit(self.path, self.name, self.collidable, self.print_priority, self.color, self.pos.x, self.pos.y)
        return copy


class TextUnit(Unit):

    def __init__(self, text, name, max_width, color=curses.COLOR_WHITE):
        Unit.__init__(self, '', name, color=color, text=True)
        self.raw = text
        self.max_width = max_width
        self.centered = text.center(max_width)
        self.body = self.build_unit([self.centered])
        self.width = v.Vector(len(self.centered), 0)
        self.height = v.Vector(0, 1)

    def refresh(self):
        self.centered = self.raw.center(self.max_width)
        for pixel, pixel2 in zip(self.body, self.centered):
            pixel.symbol = pixel2