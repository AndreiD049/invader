#! /usr/bin/python3

import logging

logging.basicConfig(filename='./app_log.txt', level = logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')


class Bitmap:

    def __init__(self, width, height):
        self.bitmap = self.init_bitmap(width, height)

    @staticmethod
    def init_bitmap(width, height):
        result = []
        for w in range(width):
            result.append([])
            for h in range(height):
                result[w].append(None)

        return result

    def print_unit(self, unit, whole):
        for pixel in unit.body:
            # logging.debug('pixel %s - %s' % (pixel.abs_pos.x, pixel.abs_pos.y))
            current = self.bitmap[pixel.abs_pos.x][pixel.abs_pos.y]
            if not pixel.is_empty():
                if current is None or pixel.print_priority > current.print_priority:
                    if pixel.parent_name == 'invader' and current is not None and current.print_priority > 0:
                        unit.collided = True
                    self.bitmap[pixel.abs_pos.x][pixel.abs_pos.y] = pixel
            elif whole:
                self.bitmap[pixel.abs_pos.x][pixel.abs_pos.y] = pixel

    def print_units(self, units, main, whole=False):
        self.clear_bitmap()
        for unit in units:
            self.print_unit(unit, whole)
        self.print_unit(main, whole)

    def clear_bitmap(self):
        for x in range(len(self.bitmap)):
            for y in range(len(self.bitmap[x])):
                self.bitmap[x][y] = None

    def print_bitmap(self):
        result = ''
        for i, row in enumerate(self.bitmap):
            result += 'Row %s\n' % i
            for i, pixel in enumerate(row):
                if pixel is not None:
                    result += '\tCol %s: %s\n' % (i, pixel.parent_name)
                else:
                    result += '\tCol %s: 0\n' % i
        return result

