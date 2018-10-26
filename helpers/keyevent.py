#! /usr/bin/python3

import logging

logging.basicConfig(filename='app_log.txt', level = logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')

f = open('./app_log.txt', 'w')
f.write('')
f.close()


class KeyEventLogger:
    MAX_RELEASE = 7

    def __init__(self):
        self.release_count = self.MAX_RELEASE
        self.pressed = -1
        self.released = -1
        self.release_queue = []

    def update(self, pressed):
        if self.pressed != pressed:
            if self.pressed != -1:
                self.release_queue.append(self.pressed)
            self.pressed = pressed

        self.released = -1

        if self.release_count == 0:
            self.released = self.release_queue.pop()
            self.release_count = self.MAX_RELEASE
        elif len(self.release_queue) > 0 and self.pressed != self.release_queue[0]:
            self.release_count -= 1
        else:
            self.release_count = self.MAX_RELEASE

    def __str__(self):
        return '============================\npressed: %s\nreleased: %s' \
               '\nqueue: %s\ncount: %s' % (self.pressed, self.released,
                                           self.release_queue, self.release_count)


if __name__ == '__main__':
    test = KeyEventLogger()
    test.update(258)
    for i in range(8):
        test.update(-1)
    for i in range(10):
        test.update(258)
    print(test)

