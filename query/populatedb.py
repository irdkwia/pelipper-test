import sqlite3

DIR_DOWN = 0
DIR_UP = 1

DEFAULT_SKY = False
DEFAULT_TIMEDARK = False
GABITE = False
SPEP_TEST = False
DUNGEON_DATA = False
DEFAULT_WII = False


con = sqlite3.connect("../database/pelipper.db")
cur = con.cursor()

if DEFAULT_WII:
    cur.execute(
        """
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("ZH5ufUAag38i6EJn", "pokedngnwii", "0", 2, 0)
    """
    )

if DEFAULT_SKY:
    cur.execute(
        """
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("HauZn7x2QjAJGzPC", "pokedungeonds", "8", 2, 0)
    """
    )

    cur.execute(
        """
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("AyCuHrGSJMKV4qja", "pokedungeonds", "1", 2, 0)
    """
    )

    cur.execute(
        """
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("6wByfR3qMdV7ztsh", "pokedungeonds", "0", 2, 0)
    """
    )

if DEFAULT_TIMEDARK:
    cur.execute(
        """
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("JtzPrHhkBeiuyjfA", "pokedungeonds", "8", 0, 0)
    """
    )
    cur.execute(
        """
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("VFUXYijc4Bbg8mQJ", "pokedungeonds", "1,2,3,4,5", 0, 0)
    """
    )
    cur.execute(
        """
        INSERT INTO wmgamelist (passwd, prefix, lang, version, udate)
        VALUES ("FYm6NkH74vRys59T", "pokedungeonds", "0", 0, 0)
    """
    )

if GABITE:
    cur.execute(
        """
        INSERT INTO wmpasslist (wid, data, version, udate)
        VALUES (9997, ?, 0, 0)
    """,
        (b"\x64\x04\x0b\x58\x70\x41\x1e\x03\x80\x43\xfc\xa3\x2d\x05",),
    )
    cur.execute(
        """
        INSERT INTO wmpasslist (wid, data, version, udate)
        VALUES (9998, ?, 2, 0)
    """,
        (b"\x64\x04\x0b\x58\x00\x80\x0b\xf2\x18\x00\x1c\xe2\x1f\x6d\x29\x00\x00",),
    )

if SPEP_TEST:
    cur.execute(
        """
        INSERT INTO wmpasslist (wid, data, version, udate)
        VALUES (9999, ?, 2, 0)
    """,
        (b"\xe4\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",),
    )

if DUNGEON_DATA:
    DUNGEONS = [
        ("Test Dungeon", DIR_DOWN),
        ("Beach Cave", DIR_DOWN),
        ("Beach Cave Pit", DIR_DOWN),
        ("Drenched Bluff", DIR_DOWN),
        ("Mt. Bristle", DIR_UP),
        ("Mt. Bristle Peak", DIR_UP),
        ("Waterfall Cave", DIR_DOWN),
        ("Apple Woods", DIR_UP),
        ("Craggy Coast", DIR_DOWN),
        ("Side Path", DIR_DOWN),
        ("Mt. Horn", DIR_UP),
        ("Rock Path", DIR_DOWN),
        ("Foggy Forest", DIR_UP),
        ("Forest Path", DIR_UP),
        ("Steam Cave", DIR_UP),
        ("Upper Steam Cave", DIR_UP),
        ("Steam Cave Peak", DIR_UP),
        ("Amp Plains", DIR_UP),
        ("Far Amp Plains", DIR_UP),
        ("Amp Clearing", DIR_DOWN),
        ("Northern Desert", DIR_UP),
        ("Quicksand Cave", DIR_DOWN),
        ("Quicksand Pit", DIR_DOWN),
        ("Underground Lake", DIR_DOWN),
        ("Crystal Cave", DIR_DOWN),
        ("Crystal Crossing", DIR_DOWN),
        ("Crystal Lake", DIR_DOWN),
        ("Chasm Cave", DIR_DOWN),
        ("Dark Hill", DIR_UP),
        ("Sealed Ruin", DIR_DOWN),
        ("Deep Sealed Ruin", DIR_DOWN),
        ("Sealed Ruin Pit", DIR_DOWN),
        ("Dusk Forest", DIR_UP),
        ("Deep Dusk Forest", DIR_UP),
        ("Treeshroud Forest", DIR_UP),
        ("Brine Cave", DIR_DOWN),
        ("Lower Brine Cave", DIR_DOWN),
        ("Brine Cave Pit", DIR_DOWN),
        ("Hidden Land", DIR_UP),
        ("Hidden Highland", DIR_UP),
        ("Old Ruins", DIR_UP),
        ("Temporal Tower", DIR_UP),
        ("Temporal Spire", DIR_UP),
        ("Temporal Pinnacle", DIR_UP),
        ("Mystifying Forest", DIR_UP),
        ("Mystifying Forest Clearing", DIR_UP),
        ("Blizzard Island", DIR_UP),
        ("Crevice Cave", DIR_DOWN),
        ("Lower Crevice Cave", DIR_DOWN),
        ("Crevice Cave Pit", DIR_DOWN),
        ("Surrounded Sea", DIR_DOWN),
        ("Miracle Sea", DIR_DOWN),
        ("Deep Miracle Sea", DIR_DOWN),
        ("Miracle Seabed", DIR_DOWN),
        ("Ice Aegis Cave", DIR_DOWN),
        ("Regice Chamber", DIR_DOWN),
        ("Rock Aegis Cave", DIR_DOWN),
        ("Regirock Chamber", DIR_DOWN),
        ("Steel Aegis Cave", DIR_DOWN),
        ("Registeel Chamber", DIR_DOWN),
        ("Aegis Cave Pit", DIR_DOWN),
        ("Regigigas Chamber", DIR_DOWN),
        ("Mt. Travail", DIR_UP),
        ("The Nightmare", DIR_DOWN),
        ("Spacial Rift", DIR_DOWN),
        ("Deep Spacial Rift", DIR_DOWN),
        ("Spacial Rift Bottom", DIR_DOWN),
        ("Dark Crater", DIR_DOWN),
        ("Deep Dark Crater", DIR_DOWN),
        ("Dark Crater Pit", DIR_DOWN),
        ("Concealed Ruins", DIR_DOWN),
        ("Deep Concealed Ruins", DIR_DOWN),
        ("Marine Resort", DIR_UP),
        ("Bottomless Sea", DIR_DOWN),
        ("Bottomless Sea Depths", DIR_DOWN),
        ("Shimmer Desert", DIR_UP),
        ("Shimmer Desert Pit", DIR_UP),
        ("Mt. Avalanche", DIR_UP),
        ("Mt. Avalanche Peak", DIR_UP),
        ("Giant Volcano", DIR_UP),
        ("Giant Volcano Peak", DIR_UP),
        ("World Abyss", DIR_DOWN),
        ("World Abyss Pit", DIR_DOWN),
        ("Sky Stairway", DIR_UP),
        ("Sky Stairway Apex", DIR_UP),
        ("Mystery Jungle", DIR_UP),
        ("Deep Mystery Jungle", DIR_UP),
        ("Serenity River", DIR_DOWN),
        ("Landslide Cave", DIR_DOWN),
        ("Lush Prairie", DIR_UP),
        ("Tiny Meadow", DIR_UP),
        ("Labyrinth Cave", DIR_DOWN),
        ("Oran Forest", DIR_UP),
        ("Lake Afar", DIR_DOWN),
        ("Happy Outlook", DIR_DOWN),
        ("Mt. Mistral", DIR_UP),
        ("Shimmer Hill", DIR_UP),
        ("Lost Wilderness", DIR_DOWN),
        ("Midnight Forest", DIR_DOWN),
        ("Zero Isle North", DIR_DOWN),
        ("Zero Isle East", DIR_DOWN),
        ("Zero Isle West", DIR_DOWN),
        ("Zero Isle South", DIR_DOWN),
        ("Zero Isle Center", DIR_DOWN),
        ("Destiny Tower", DIR_UP),
        ("Dummy", DIR_DOWN),
        ("Dummy", DIR_DOWN),
        ("Oblivion Forest", DIR_DOWN),
        ("Treacherous Waters", DIR_DOWN),
        ("Southeastern Islands", DIR_DOWN),
        ("Inferno Cave", DIR_DOWN),
        ("1st Station Pass", DIR_UP),
        ("2nd Station Pass", DIR_UP),
        ("3rd Station Pass", DIR_UP),
        ("4th Station Pass", DIR_UP),
        ("5th Station Pass", DIR_UP),
        ("6th Station Pass", DIR_UP),
        ("7th Station Pass", DIR_UP),
        ("8th Station Pass", DIR_UP),
        ("9th Station Pass", DIR_UP),
        ("Sky Peak Summit Pass", DIR_UP),
        ("5th Station Clearing", DIR_UP),
        ("Sky Peak Summit", DIR_UP),
        ("Star Cave", DIR_DOWN),
        ("Deep Star Cave", DIR_DOWN),
        ("Deep Star Cave", DIR_DOWN),
        ("Star Cave Depths", DIR_DOWN),
        ("Star Cave Pit", DIR_DOWN),
        ("Murky Forest", DIR_UP),
        ("Eastern Cave", DIR_DOWN),
        ("Fortune Ravine", DIR_DOWN),
        ("Fortune Ravine Depths", DIR_DOWN),
        ("Fortune Ravine Pit", DIR_DOWN),
        ("Barren Valley", DIR_UP),
        ("Deep Barren Valley", DIR_UP),
        ("Barren Valley Clearing", DIR_UP),
        ("Dark Wasteland", DIR_UP),
        ("Temporal Tower", DIR_UP),
        ("Temporal Spire", DIR_UP),
        ("Dusk Forest", DIR_UP),
        ("Black Swamp", DIR_UP),
        ("Spacial Cliffs", DIR_UP),
        ("Dark Ice Mountain", DIR_UP),
        ("Dark Ice Mountain Peak", DIR_UP),
        ("Dark Ice Mountain Pinnacle", DIR_UP),
        ("Icicle Forest", DIR_UP),
        ("Vast Ice Mountain", DIR_UP),
        ("Vast Ice Mountain Peak", DIR_UP),
        ("Vast Ice Mountain Pinnacle", DIR_UP),
        ("Southern Jungle", DIR_UP),
        ("Boulder Quarry", DIR_DOWN),
        ("Deep Boulder Quarry", DIR_DOWN),
        ("Boulder Quarry Clearing", DIR_DOWN),
        ("Right Cave Path", DIR_DOWN),
        ("Left Cave Path", DIR_DOWN),
        ("Limestone Cavern", DIR_DOWN),
        ("Deep Limestone Cavern", DIR_DOWN),
        ("Limestone Cavern Depths", DIR_DOWN),
        ("Spring Cave", DIR_DOWN),
        ("Upper Spring Cave", DIR_DOWN),
        ("Upper Spring Cave", DIR_DOWN),
        ("Middle Spring Cave", DIR_DOWN),
        ("Lower Spring Cave", DIR_DOWN),
        ("Spring Cave Depths", DIR_DOWN),
        ("Spring Cave Pit", DIR_DOWN),
        ("Dummy", DIR_UP),
        ("Dummy", DIR_UP),
        ("Dummy", DIR_DOWN),
        ("Dummy", DIR_UP),
        ("Dummy", DIR_DOWN),
        ("Dummy", DIR_DOWN),
        ("Dummy", DIR_DOWN),
        ("Dummy", DIR_DOWN),
        ("Dummy", DIR_DOWN),
        ("Star Cave", DIR_DOWN),
        ("Shaymin Village", DIR_DOWN),
        ("Armaldo's Shelter", DIR_DOWN),
        ("Luminous Spring", DIR_DOWN),
        ("Hot Spring", DIR_DOWN),
        ("Rescue", DIR_DOWN),
        ("Normal/Fly Maze", DIR_DOWN),
        ("Dark/Fire Maze", DIR_DOWN),
        ("Rock/Water Maze", DIR_DOWN),
        ("Grass Maze", DIR_DOWN),
        ("Elec/Steel Maze", DIR_DOWN),
        ("Ice/Ground Maze", DIR_DOWN),
        ("Fight/Psych Maze", DIR_DOWN),
        ("Poison/Bug Maze", DIR_DOWN),
        ("Dragon Maze", DIR_DOWN),
        ("Ghost Maze", DIR_DOWN),
        ("Explorer Maze", DIR_DOWN),
        ("Final Maze", DIR_DOWN),
    ]
    for did, dinfo in enumerate(DUNGEONS):
        cur.execute(
            """
            INSERT INTO dungeondata (did, name, direction, udate)
            VALUES (?, ?, ?, 0)
        """,
            (did, dinfo[0], dinfo[1]),
        )

con.commit()
con.close()
