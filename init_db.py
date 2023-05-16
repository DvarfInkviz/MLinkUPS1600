import sqlite3
import os
from datetime import datetime


basedir = os.path.abspath(os.path.dirname(__file__))
connection = sqlite3.connect(os.path.join(basedir, "database.db"))

with open(os.path.join(basedir, 'schema.sql')) as f:
    connection.executescript(f.read())

cur = connection.cursor()
salt = b'$2a$12$/VFqyH0kO30PQt5Yv6TF6.'
cur.execute("INSERT INTO users (created, login, password, fullname, job_title, priority, permissions) "
            "VALUES (?,?,?,?,?,?,?)",
            (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 'sadmin',
             '$2a$12$/VFqyH0kO30PQt5Yv6TF6.ze7gIEfRekBQYwOAz3eqZksEEjDt4eK', 'Lyashko Alexander',
             'Администратор системы', 50, '11111111')
            )

cur.execute("INSERT INTO users (created, login, password, fullname, job_title, priority, permissions) "
            "VALUES (?,?,?,?,?,?,?)",
            (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 'test',
             '$2a$12$/VFqyH0kO30PQt5Yv6TF6.Is2r/zF0wYokmEApJGWWUkaqivdaiRq', 'Наблюдатель',
             'Наблюдатель', 1, '11111111')
            )

cur.execute("INSERT INTO users (created, login, password, fullname, job_title, priority, permissions) "
            "VALUES (?,?,?,?,?,?,?)",
            (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 'test2',
             '$2a$12$/VFqyH0kO30PQt5Yv6TF6.Is2r/zF0wYokmEApJGWWUkaqivdaiRq', 'Оператор',
             'Оператор', 2, '11111111')
            )

cur.execute("INSERT INTO ups_settings (id) VALUES (?)", (1, ))
connection.commit()
connection.close()
