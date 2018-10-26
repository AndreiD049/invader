#! /usr/bin/python3

import sys
import logging

logging.basicConfig(filename='./../app_log.txt', level = logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')
sys.path.append('./..')

import main

stage = main.Stage()
inv1 = main.Unit('./../units/invader', 'invader1')
inv2 = main.Unit('./../units/test', 'invader2')
inv3 = main.Unit('./../units/test', 'invader3')

stage.add_unit(inv1, 100, 0, main=True)
stage.add_unit(inv2, 30, 0)
stage.add_unit(inv3, 60, 0)
stage.draw_units()
while True:
    stage.mv_unit(inv2, -1, 0)
    stage.mv_unit(inv1, 1, 0)
    stage.mv_unit(inv3, 1, 1)
    stage.draw_units()
    if stage.main_unit.hitbox.check_collision(inv2.hitbox):
        logging.debug('Collision at (%s, %s, %s) and (%s, %s, %s)' % (inv1.pos, inv1.width, inv1.height, inv2.pos, inv2.width, inv2.height))
        break
