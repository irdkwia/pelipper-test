import sqlite3, os

os.makedirs("database", exist_ok=False)

con = sqlite3.connect("database/pelipper.db")

cur = con.cursor()

cur.execute("""
    CREATE TABLE globalprofile (
        token TEXT UNIQUE,
        challenge TEXT,
        gbsr TEXT NOT NULL PRIMARY KEY,
        game TEXT NOT NULL,
        userid INTEGER NOT NULL UNIQUE,
        profileid INTEGER NOT NULL UNIQUE,
        nick TEXT,
        uniquenick TEXT,
        email TEXT,
        firstname TEXT,
        lastname TEXT,
        icquin TEXT,
        homepage TEXT,
        zipcode TEXT,
        countrycode TEXT,
        lon TEXT,
        lat TEXT,
        loc TEXT,
        birthday TEXT,
        sex TEXT,
        pmask TEXT,
        aim TEXT,
        pic TEXT,
        occ TEXT,
        ind TEXT,
        mar TEXT,
        chc TEXT,
        i1 TEXT,
        o1 TEXT,
        conn TEXT,
        sig TEXT,
        udate INTEGER NOT NULL
    )
""")


cur.execute("""
    CREATE TABLE profile (
        currenthash TEXT,
        pid INTEGER NOT NULL PRIMARY KEY,
        game INTEGER NOT NULL,
        lang INTEGER NOT NULL,
        email TEXT NOT NULL,
        flags INTEGER NOT NULL,
        team TEXT NOT NULL,
        ccode INTEGER NOT NULL,
        scode INTEGER NOT NULL,
        unified INTEGER NOT NULL,
        udate INTEGER NOT NULL
    )
""")

cur.execute("""
    CREATE TABLE teamdata (
        pid INTEGER NOT NULL PRIMARY KEY,
        tid INTEGER NOT NULL UNIQUE,
        rank INTEGER NOT NULL,
        lang INTEGER NOT NULL,
        team TEXT NOT NULL,
        pkmn BLOB NOT NULL,
        udate INTEGER NOT NULL
    )
""")


cur.execute("""
    CREATE TABLE rescuerequest (
        rid INTEGER NOT NULL PRIMARY KEY,
        uid INTEGER NOT NULL UNIQUE,
        code INTEGER NOT NULL,
        seed INTEGER NOT NULL,
        dungeon INTEGER NOT NULL,
        floor INTEGER NOT NULL,
        game INTEGER NOT NULL,
        lang INTEGER NOT NULL,
        team TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        completed INTEGER NOT NULL,
        requested INTEGER NOT NULL,
        udate INTEGER NOT NULL
    )
""")


cur.execute("""
    CREATE TABLE rescueaok (
        rid INTEGER NOT NULL PRIMARY KEY,
        uresp INTEGER NOT NULL,
        code INTEGER NOT NULL,
        item BLOB NOT NULL,
        pkmn BLOB NOT NULL,
        game INTEGER NOT NULL,
        lang INTEGER NOT NULL,
        team TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        udate INTEGER NOT NULL
    )
""")


cur.execute("""
    CREATE TABLE rescuethanks (
        rid INTEGER NOT NULL PRIMARY KEY,
        code INTEGER NOT NULL,
        item BLOB NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        claimed INTEGER NOT NULL,
        udate INTEGER NOT NULL
    )
""")
cur.execute("""
    CREATE TABLE buddylist (
        pid INTEGER NOT NULL,
        buddy INTEGER NOT NULL,
        udate INTEGER NOT NULL,
        PRIMARY KEY("pid","buddy")
    )
""")

con.commit()
con.close()
