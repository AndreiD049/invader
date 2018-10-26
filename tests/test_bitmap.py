#! /ust/bin/python3

import helpers.bitmap as b
import main

test = b.Bitmap(100, 30)
unit = main.Unit('../units/invader', 'invader')
test.print_to_bm(unit)
print(len(test.bitmap[0]))
print(len(test.bitmap))
print(test.bitmap)