#! /usr/bin/python3

import curses
from curses.textpad import Textbox, rectangle


def main(stdscr):
    stdscr.addstr(0, 0, 'Enter message: ')
    editwin = curses.newwin(1, 25, 2, 1)
    rectangle(stdscr, 1, 0, 3, 26)
    stdscr.nodelay(True)
    stdscr.refresh()
    box = Textbox(editwin)

    # box.edit()

    while True:
        k = stdscr.getch()
        if k == 10:
            curses.curs_set(1)
            box.edit()
        curses.curs_set(0)
        stdscr.refresh()

curses.wrapper(main)