import sqlite3

con = sqlite3.connect("../database/pelipper.db")

cur = con.cursor()

cur.execute(
    """
    INSERT INTO wmpasslist (wid, data, prefix, version, udate)
    VALUES (?, ?, ?, 2, 0)
""",
    (
        1,  # Put an ID (this is an unique arbitrary number to identify the wonder mail)
        b"\xe4\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",  # Put the actual bytes data of the wonder mail
        "wpaj",  # The game's code lower case
    ),
)

con.commit()
con.close()
