import sqlite3, os, sys

if len(sys.argv)>1:
    listprefix = [x+"_" for x in sys.argv[1:]]
else:
    listprefix = [""]

os.makedirs("database", exist_ok=True)

con = sqlite3.connect("database/pelipper.db")

cur = con.cursor()

for prefix in listprefix:
    if prefix=="":
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
            CREATE TABLE buddylist (
                pid INTEGER NOT NULL,
                buddy INTEGER NOT NULL,
                udate INTEGER NOT NULL,
                PRIMARY KEY("pid","buddy")
            )
        """)

        cur.execute("""
            CREATE TABLE wmgamelist (
                passwd TEXT NOT NULL PRIMARY KEY,
                prefix TEXT NOT NULL,
                lang TEXT NOT NULL
            )
        """)

    cur.execute("""
        CREATE TABLE %steamdata (
            pid INTEGER NOT NULL PRIMARY KEY,
            tid INTEGER NOT NULL UNIQUE,
            rank INTEGER NOT NULL,
            lang INTEGER NOT NULL,
            team TEXT NOT NULL,
            pkmn BLOB NOT NULL,
            private INTEGER NOT NULL,
            udate INTEGER NOT NULL
        )
    """ % prefix)


    cur.execute("""
        CREATE TABLE %srescuerequest (
            pid INTEGER NOT NULL,
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
            private INTEGER NOT NULL,
            udate INTEGER NOT NULL
        )
    """ % prefix)


    cur.execute("""
        CREATE TABLE %srescueaok (
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
    """ % prefix)


    cur.execute("""
        CREATE TABLE %srescuethanks (
            rid INTEGER NOT NULL PRIMARY KEY,
            code INTEGER NOT NULL,
            item BLOB NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            claimed INTEGER NOT NULL,
            udate INTEGER NOT NULL
        )
    """ % prefix)

    cur.execute("""
        CREATE TABLE %swmpasslist (
            wid INTEGER NOT NULL PRIMARY KEY,
            data BLOB NOT NULL
        )
    """ % prefix)

con.commit()
con.close()
