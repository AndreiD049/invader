#! /usr/bin/python3

import curses
from curses.textpad import Textbox, rectangle
import helpers.units as u
import helpers.vector as v
import logging

logging.basicConfig(filename='app_log.txt', level = logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')

f = open('./app_log.txt', 'w')
f.write('')
f.close()


class Menu():

    def __init__(self, stage, options, logopath):
        try:
            max_w = len(max(options, key=lambda x: len(x)))
        except ValueError:
            max_w = 0
        self.options = [Option(o, 'option', max_w) for o in options]
        self.stage = stage
        self.selected_index = 0
        self.logo = u.Unit(logopath, 'logo')

        self.action_map = {'10': self.select,
                           '258': self.next,
                           '259': self.prev,
                           '-1': self.do_nothing}

        self.change_focus(0)

    def do_nothing(self):
        pass

    def select(self):
        return True

    def next(self):
        self.change_focus((self.selected_index + 1) % len(self.options))
        return False

    def prev(self):
        self.change_focus((self.selected_index - 1) % len(self.options))

    def change_focus(self, option_nr):
        for opt in self.options:
            index = self.options.index(opt)
            if index == option_nr:
                # logging.debug('Changing the index from %s to %s' % (self.selected_index, index))
                self.selected_index = index
                opt.focus = True
                opt.color = 'selected'
                self.pixel_color_change(opt, 'selected')
            else:
                opt.focus = False
                opt.color = curses.COLOR_WHITE
                self.pixel_color_change(opt, curses.COLOR_WHITE)

    def draw_options(self, x, y, logo):
        # param: x is the middle of the screen
        posy = y
        mid = x - int(logo.width.length() / 2)
        self.stage.add_unit(logo, mid, posy)
        posy -= 1
        for opt in self.options:
            mid = x - int(opt.width.length() / 2)
            posy -= 1
            # logging.debug('posy - %s' % posy)
            self.stage.add_unit(opt, mid, posy)
        self.stage.bitmap.print_units(self.stage.units, logo, True)

        return self.stage.draw_units2(False)

    @staticmethod
    def pixel_color_change(opt, color):
        for pixel in opt.body:
            pixel.color = color


class InputMenu(Menu):

    def __init__(self, stage, inputs, options, logopath):
        self.inputs = [InputUnit(i, 'input', 25) for i in inputs]
        Menu.__init__(self, stage, options, logopath)
        curses.ungetch(258)

    def draw_options(self, x, y, logo):
        # param: x is the middle of the screen
        posy = y
        mid = x - int(logo.width.length() / 2)
        self.stage.add_unit(logo, mid, posy)
        posy -= 2
        for inp in self.inputs:
            mid = x - int(inp.width.length() + (inp.max_ch / 2))
            posy -= 1
            self.stage.add_unit(inp, mid, posy)
            if inp.textbox is None:
                # logging.debug('is none')
                inp.add_textbox(mid, posy, self.stage)
        posy -= 2
        for opt in self.options:
            mid = x - int(opt.width.length() / 2)
            posy -= 1
            self.stage.add_unit(opt, mid, posy)
        self.stage.bitmap.print_units(self.stage.units, logo, True)

        return self.stage.draw_units2(False)

    def change_focus(self, option_nr):
        all = self.inputs + self.options
        for opt in all:
            index = all.index(opt)
            if index == option_nr:
                self.selected_index = index
                opt.focus = True
                if opt.name != 'input':
                    opt.color = 'selected'
                    self.pixel_color_change(opt, 'selected')
                elif opt.textbox is not None:
                    curses.curs_set(1)
                    opt.value = opt.textbox.textbox.edit()
                    curses.curs_set(0)
                    # logging.debug(opt.value)
                    curses.ungetch(10)
            else:
                opt.focus = False
                opt.color = curses.COLOR_WHITE
                self.pixel_color_change(opt, curses.COLOR_WHITE)

    def next(self):
        self.change_focus((self.selected_index + 1) % len(self.options + self.inputs))
        return False

    def prev(self):
        self.change_focus((self.selected_index - 1) % len(self.options + self.inputs))


class Option(u.TextUnit):

    def __init__(self, text, name, max_width, focus=False, color=curses.COLOR_WHITE):
        u.TextUnit.__init__(self, text, name, max_width, color)
        self.focus = focus


class InputUnit(Option):

    def __init__(self, text, name, max_ch, focus=False, color=curses.COLOR_WHITE):
        Option.__init__(self, text, name, len(text), focus, color)
        self.textbox = None
        self.max_ch = max_ch
        self.bl = v.Vector(0, 0)
        self.br = v.Vector(0, 0)

    def add_textbox(self, x, y, stage):
        posy = stage.height.length() - 1 - y
        editwin = curses.newwin(1, self.max_ch - 1, posy, x + len(self.centered) + 1)
        self.textbox = InputField(editwin, x + len(self.centered), posy - 1,
                                  x + self.max_ch + len(self.centered), posy + 1)
        stage.inputs.append(self.textbox)


class InputField:

    def __init__(self, win, ux, uy, bx, by):
        self.textbox = Textbox(win)
        self.ul = v.Vector(ux, uy)
        self.br = v.Vector(bx, by)
        self.value = ''