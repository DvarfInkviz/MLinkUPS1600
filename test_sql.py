import os
import sqlite3
import math


def get_db_connection():
    basedir = os.path.abspath(os.path.dirname(__file__))
    # connection = sqlite3.connect(os.path.join(basedir, "database_1708.db"))
    connection = sqlite3.connect("/var/www/web-ups1600/database_1708.db")
    connection.row_factory = sqlite3.Row
    return connection


conn = get_db_connection()
pids = conn.execute('SELECT * FROM pids').fetchall()
for pid in pids:
    for p in pid:
        print(p, end=', ')
print()
conn.execute('UPDATE pids SET video1 = ? WHERE id = ?',
             ('FFFF', 1,))
conn.commit()
db = []
pids = conn.execute('SELECT * FROM pids').fetchall()
# plc_set = conn.execute('SELECT ss_lat, ss_lon, ss_alt FROM plc_settings WHERE id =1').fetchone()
# print(plc_set[0], plc_set[1], plc_set[2])

for pid in pids:
    for p in pid:
        print(p, end=', ')
#     db.append([user[0], user[3], user[6], user[7], ])
# print(db)
# _sats = conn.execute('SELECT COUNT(*) FROM sats WHERE orbita = 0').fetchone()[0]
conn.close()
# print(_sats)

