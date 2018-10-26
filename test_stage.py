import sqlite3


def connect():
    conn = sqlite3.connect('./data/data.db')
    c = conn.cursor()
    try:
        c.execute('CREATE TABLE IF NOT EXISTS Players (id int primary key, name text, score integer, last int)')
    except:
        pass
    return conn, c


conn, c = connect()
try:
    next_index = c.execute('SELECT * FROM Players ORDER BY id DESC LIMIT 1').fetchone()[0] + 1
except TypeError:
    next_index = 0

name = input('Please inter a name: \n')

c.execute('INSERT INTO Players (id, name, score, last) VALUES (?, ?, 10, 0)', (next_index, name))

rows = c.execute('SELECT * FROM Players')

print(rows.fetchall())

conn.commit()
conn.close()