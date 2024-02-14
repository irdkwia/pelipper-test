import sqlite3

DEFAULT_SKY = True
DEFAULT_TIMEDARK = True
GABITE = True
SPEP_TEST = False

con = sqlite3.connect("database/pelipper.db")
cur = con.cursor()

if DEFAULT_SKY:
    cur.execute("""
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("HauZn7x2QjAJGzPC", "pokedungeonds", "8", 2, 0)
    """)

    cur.execute("""
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("AyCuHrGSJMKV4qja", "pokedungeonds", "1", 2, 0)
    """)

    cur.execute("""
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("6wByfR3qMdV7ztsh", "pokedungeonds", "0", 2, 0)
    """)

if DEFAULT_TIMEDARK:
    cur.execute("""
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("JtzPrHhkBeiuyjfA", "pokedungeonds", "8", 0, 0)
    """)
    cur.execute("""
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("VFUXYijc4Bbg8mQJ", "pokedungeonds", "1,2,3,4,5", 0, 0)
    """)
    cur.execute("""
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("FYm6NkH74vRys59T", "pokedungeonds", "0", 0, 0)
    """)
    
if GABITE:
    cur.execute("""
        INSERT INTO wmpasslist (wid, data, version, udate)
        VALUES (9997, ?, 0, 0)
    """, (b'\x64\x04\x0b\x58\x70\x41\x1e\x03\x80\x43\xfc\xa3\x2d\x05',))
    cur.execute("""
        INSERT INTO wmpasslist (wid, data, version, udate)
        VALUES (9998, ?, 2, 0)
    """, (b'\x64\x04\x0b\x58\x00\x80\x0b\xf2\x18\x00\x1c\xe2\x1f\x6d\x29\x00\x00',))

if SPEP_TEST:
    cur.execute("""
        INSERT INTO wmpasslist (wid, data, version, udate)
        VALUES (9999, ?, 2, 0)
    """, (b'\xe4\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',))

con.commit()
con.close()
