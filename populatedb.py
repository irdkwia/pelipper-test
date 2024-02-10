import sqlite3

DEFAULT = True
GABITE = True
SPEP_TEST = False

con = sqlite3.connect("database/pelipper.db")
cur = con.cursor()

if DEFAULT:
    cur.execute("""
        INSERT INTO wmgamelist (passwd, prefix, lang, udate)
        VALUES ("HauZn7x2QjAJGzPC", "pokedungeonds", 8, 0)
    """)

    cur.execute("""
        INSERT INTO wmgamelist (passwd, prefix, lang, udate)
        VALUES ("AyCuHrGSJMKV4qja", "pokedungeonds", 1, 0)
    """)

    cur.execute("""
        INSERT INTO wmgamelist (passwd, prefix, lang, udate)
        VALUES ("6wByfR3qMdV7ztsh", "pokedungeonds", 0, 0)
    """)

if GABITE:
    cur.execute("""
        INSERT INTO wmpasslist (wid, data, udate)
        VALUES (9998, ?, 0)
    """, (b'\x64\x04\x0b\x58\x00\x80\x0b\xf2\x18\x00\x1c\xe2\x1f\x6d\x29\x00\x00',))

if SPEP_TEST:
    cur.execute("""
        INSERT INTO wmpasslist (wid, data, udate)
        VALUES (9999, ?, 0)
    """, (b'\xe4\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',))

con.commit()
con.close()
