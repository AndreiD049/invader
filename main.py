#! /usr/bin/python3

import curses, logging, random
import helpers.vector as v
import helpers.bitmap as b
import helpers.menu as m
import helpers.units as u
import helpers.keyevent as k
import helpers.connection as c
from time import sleep
from curses.textpad import rectangle

logging.basicConfig(filename='app_log.txt', level = logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')

f = open('./app_log.txt', 'w')
f.write('')
f.close()


class Stage:

    def __init__(self, stdscr):
        curses.curs_set(0)
        curses.start_color()
        y, x = stdscr.getmaxyx()

        self.field = stdscr
        self.height = v.Vector(0, y - 1)
        self.width = v.Vector(x, 0)
        self.main_unit = None
        self.units = []
        self.inputs = []
        self.bg_units = []
        self.floor_level = v.Vector(0, 0)
        self.bitmap = b.Bitmap(self.width.x, self.height.y - 1)
        self.palette = Palette()
        self.keyevent = k.KeyEventLogger()

    def normalize(self, req_pos, max_pos, unit, vertical=False):
        result = req_pos
        if req_pos < 0:
            result = 0
        elif req_pos > max_pos:
            result = max_pos
        elif vertical and req_pos < self.floor_level.y + 3 and unit.name != 'floor' and unit.name != 'option':
            result = self.floor_level.y + 3
        return result

    def add_unit(self, unit, x, y, main=False):
        # Unit position is normalized so it doesnt go beyond screen
        unit.pos.x = self.normalize(x, (self.width - unit.width).x, unit)
        unit.pos.y = self.normalize(y, (self.height - unit.height).y, unit, vertical=True)
        if main:
            self.main_unit = unit
        else:
            self.units.append(unit)

        # getting curses positioning (reversing the y axis)
        curses_pos_y = self.height.length() - 1 - unit.pos.y
        for pixel in unit.body:
            pixel.abs_pos.x = unit.pos.x + pixel.rel_pos.x
            pixel.abs_pos.y = curses_pos_y - pixel.rel_pos.y

    def mv_unit(self, unit, x, y):
        # Unit position is normalized so it doesnt go beyond screen
        unit.pos.x = self.normalize(unit.pos.x + x, (self.width - unit.width).x, unit)
        unit.pos.y = self.normalize(unit.pos.y + y, (self.height - unit.height).y, unit, vertical=True)

        # getting curses positioning (reversing y axis)
        curses_pos_y = self.height.length() - 1 - unit.pos.y

        for pixel in unit.body:
            pixel.abs_pos.x = unit.pos.x + pixel.rel_pos.x
            pixel.abs_pos.y = curses_pos_y - pixel.rel_pos.y

    def draw_unit(self, unit):
        for pixel in unit.body:
            if not pixel.is_empty():
                self.field.addch(pixel.abs_pos.y, pixel.abs_pos.x, pixel.symbol)

    def draw_units(self):
        self.field.clear()
        self.draw_unit(self.main_unit)
        for unit in self.units:
            self.draw_unit(unit)
            if unit.name != 'floor' and unit.pos.x < self.main_unit.pos.x:
                self.draw_unit(self.main_unit)
            if unit.name == 'bg' and unit.pos.x < (self.main_unit.pos.x + self.main_unit.width.x):
                self.draw_unit(self.main_unit)

        return self.frame_refresh()

    def draw_units2(self, no_delay=True):
        self.field.clear()
        pixel_list = [pixel for sublist in self.bitmap.bitmap for pixel in sublist]
        for pixel in pixel_list:
            if pixel is not None:
                self.field.addstr(pixel.abs_pos.y, pixel.abs_pos.x, pixel.symbol,
                                  curses.color_pair(self.palette.palette[pixel.color]) | curses.A_BOLD)
            for inp in self.inputs:
                rectangle(self.field, inp.ul.y, inp.ul.x, inp.br.y, inp.br.x)

        return self.frame_refresh(no_delay)

    def build_floor(self, floor_level):
        self.floor_level = v.Vector(0, floor_level)
        for pixel in range(self.width.length()):
            unit = u.Unit('./units/block', 'floor', False, 0)
            self.add_unit(unit, pixel, floor_level)

    def frame_refresh(self, no_delay=True):
        self.field.refresh()
        if no_delay:
            self.field.nodelay(True)
            sleep(0.06)
        else:
            self.field.nodelay(False)
        k = self.field.getch()
        # logging.debug(k)
        self.keyevent.update(k)
        curses.flushinp()
        return self.keyevent

    def __end__(self):
        curses.nocbreak()
        self.field.keypad(False)
        curses.echo()
        curses.endwin()


class Game:

    FLOOR_LVL = 5
    velocity = v.Vector(-3, 0)

    def __init__(self, stage):

        self.options = {}
        self.inputs = {}

        self.stage = stage
        self.game_over = False
        self.main_unit = None
        self.generator = None
        self.menu = None
        self.gameover_menu = None
        self.connection = c.Connection('./data/data.db')
        last = self.connection.get_last()
        if last:
            self.player = Player(last[1], self.stage)
        else:
            self.newuser()
        self.mainmenu()

    def newuser(self):
        self.stage.inputs = []
        self.stage.units = []
        self.options = {}
        self.inputs = {'Name:': self.validate_name}
        self.menu = m.InputMenu(self.stage, self.inputs, self.options, './units/logo')
        selected = False
        while not selected:
            key = self.menu.draw_options(int(self.stage.width.length() / 2), 15, self.menu.logo)
            selected = self.menu.action_map.get(str(key.pressed), self.menu.next)()
        inp = self.inputs[self.menu.inputs[self.menu.selected_index].raw]
        inp(self.menu.inputs[self.menu.selected_index].value)

    def validate_name(self, name):
        if not self.connection.insert_value(name, 0):
            self.newuser()
        else:
            last = self.connection.get_last()
            logging.debug(last)
            self.player = Player(last[1], self.stage)
            self.mainmenu()

    def mainmenu(self):
        self.stage.inputs = []
        self.stage.units = []
        self.options = {'New Game': self.startup,
                        'Rankings': self.quit,
                        'New User': self.newuser,
                        'Quit  Game': self.quit}
        self.menu = m.Menu(self.stage, self.options.keys(), './units/logo')
        selected = False
        while not selected:
            key = self.menu.draw_options(int(self.stage.width.length() / 2), 15, self.menu.logo)
            selected = self.menu.action_map.get(str(key.pressed), self.menu.do_nothing)()
        self.options[self.menu.options[self.menu.selected_index].raw]()

    def gameover(self):
        sleep(2)
        self.stage.units = []
        # self.stage.field.clear()
        # self.stage.bitmap.clear_bitmap()
        self.options = {'Restart': self.startup,
                        'Main Menu': self.mainmenu,
                        'Quit Game': self.quit}
        self.gameover_menu = m.Menu(self.stage, self.options.keys(), './units/gameover')
        selected = False
        while not selected:
            key = self.gameover_menu.draw_options(int(self.stage.width.length() / 2), 15, self.gameover_menu.logo)
            selected = self.gameover_menu.action_map.get(str(key.pressed), self.gameover_menu.do_nothing)()
        self.options[self.gameover_menu.options[self.gameover_menu.selected_index].raw]()

    def startup(self):
        self.game_over = False
        self.stage.units = []
        self.stage.field.clear()
        self.main_unit = u.MainUnit('./units/invader', 'invader', color=curses.COLOR_RED)
        self.player = Player(self.player.name, self.stage)
        self.stage.build_floor(self.FLOOR_LVL)
        self.stage.add_unit(self.main_unit, 20, self.stage.floor_level.y, main=True)
        self.generator = Generator(self.stage, self.main_unit.width.length(), self.velocity)
        self.stage.bitmap.print_units(self.stage.units, self.main_unit)
        # send enter key to start moving the unit
        curses.ungetch(10)
        self.stage.draw_units2()

    @staticmethod
    def quit():
        exit(0)

    def check_collisions(self):
        self.stage.bitmap.print_units(self.stage.units, self.main_unit)
        if self.main_unit.collided:
            self.game_over = True

    def make_step(self):
        self.generator.generate()

        for unit in self.stage.units:
            if unit.name != 'floor':
                self.stage.mv_unit(unit, self.velocity.x, self.velocity.y)

        self.main_unit.update_velocity()
        self.stage.mv_unit(self.main_unit, self.main_unit.def_velocity.x, self.main_unit.def_velocity.y)

        # terminate jump if unit landed
        if self.main_unit.pos.y == self.stage.floor_level.y + 3:
            self.main_unit.clear_jump_arr()

        self.check_collisions()

        if self.player is not None:
            logging.debug(self.player.name)
            self.player.update_score(abs(self.velocity.x))
        key = self.stage.draw_units2()

        self.check_border_units()

        self.main_unit.action_map.get(str(key.pressed), self.main_unit.do_nothing)()
        self.main_unit.release_actions.get(str(key.released), self.main_unit.do_nothing)()

    def check_border_units(self):
        for unit in self.stage.units:
            if unit.name != 'floor' and unit.pos.x <= abs(self.velocity.x):
                self.stage.units.remove(unit)


class Generator:

    def __init__(self, stage, len, vel):
        """
        Generates the obstacles and background items
        :param len: width of the main unit
        """
        self.last_obs = 0
        self.last_bg = 0
        self.min_width = int(len * 2.5)
        self.stage = stage
        self.velocity = vel
        self.obstacles = [u.Unit('./units/cactus', 'wall', True, 1, curses.COLOR_GREEN),
                          u.BackgroundUnit('./units/bird', 'wall', True, 1, curses.COLOR_RED, ypos=(self.stage.floor_level.y + self.stage.main_unit.height.length() + 2))]
        self.background_units = [u.BackgroundUnit('./units/tree', 'bg'),
                                 u.BackgroundUnit('./units/bird', 'bg', ypos=self.stage.height.length() - 10),
                                 u.BackgroundUnit('./units/cloud', 'bg', ypos=self.stage.height.length() - 5)]

    def generate_obs(self):
        r = random.random()
        self.last_obs += abs(self.velocity.x)
        if r < 0.04 and self.last_obs > self.min_width and self.last_bg > 5:
            unit = random.choice(self.obstacles).copy()
            self.stage.add_unit(unit, 500, unit.pos.y)
            self.last_obs = 0

    def generate_bg(self):
        r = random.random()
        self.last_bg += abs(self.velocity.x)
        if r < 0.05 and self.last_bg > self.min_width  and self.last_obs > 5:
            unit = random.choice(self.background_units).copy()
            self.stage.add_unit(unit, unit.pos.x, unit.pos.y)
            self.last_bg = 0

    def generate(self):
        self.generate_bg()
        self.generate_obs()


class Palette:

    def __init__(self):
        self.palette = {curses.COLOR_WHITE: 1,
                        curses.COLOR_GREEN: 2,
                        curses.COLOR_BLUE: 3,
                        curses.COLOR_RED:4,
                        'selected': 5}
        curses.init_pair(self.palette[curses.COLOR_WHITE], curses.COLOR_WHITE, 0)
        curses.init_pair(self.palette[curses.COLOR_GREEN], curses.COLOR_GREEN, 0)
        curses.init_pair(self.palette[curses.COLOR_BLUE], curses.COLOR_BLUE, 0)
        curses.init_pair(self.palette[curses.COLOR_RED], curses.COLOR_RED, 0)
        curses.init_pair(self.palette['selected'], curses.COLOR_BLACK, curses.COLOR_YELLOW)

######################################################


class Player:

    def __init__(self, name, stage):
        self.name = name
        self.score = 0
        self.score_unit = u.TextUnit(str(self.score), 'floor', 10)
        self.place_score(stage)

    def place_score(self, stage):
        stage.add_unit(u.TextUnit(self.name, 'floor', 10), 500, stage.height.length() - 1)
        stage.add_unit(self.score_unit, 500, stage.height.length() - 2)

    def update_score(self, val):
        self.score += val
        self.score_unit.raw = str(self.score)
        self.score_unit.refresh()
        logging.debug(self.score_unit.raw)

logging.debug('Start of the program.')


def main(stdscr):
    stage = Stage(stdscr)
    game = Game(stage)
    # game.game_over = True

    while True:
        game.make_step()
        if game.game_over:
            game.gameover()


if __name__ == '__main__':
    curses.wrapper(main)
