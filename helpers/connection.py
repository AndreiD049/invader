#! /usr/bin/python3

import sqlite3


class Connection:

    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.create_table_ie()

    def create_table_ie(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Players 
                                (id int primary key, name text unique, score integer, last integer)''')
        self.conn.commit()

    def insert_value(self, name, score):
        try:
            last_index = self.cursor.execute('SELECT * FROM Players ORDER BY id DESC LIMIT 1').fetchone()[0] + 1
        except TypeError:
            last_index = 1
        try:
            self.cursor.execute('''INSERT INTO Players (id, name, score) VALUES (?, ?, ?)''', (last_index, name, score))
            self.set_last(name)
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def set_last(self, name):
        self.cursor.execute('''UPDATE Players
                            SET last = 1
                            WHERE name = ?''', (name,))
        self.cursor.execute('''UPDATE Players
                            SET last = 0
                            WHERE name <> ?''', (name,))
        self.conn.commit()

    def get_last(self):
        self.cursor.execute('''SELECT * FROM Players
                            WHERE last = 1''')
        return self.cursor.fetchone()

    def get_top(self, n):
        top = self.cursor.execute('''SELECT * FROM Players ORDER BY score DESC LIMIT 10''')
        return top.fetchall()


if __name__ == '__main__':
    test = Connection('../data/data.db')
    print(test.get_last())