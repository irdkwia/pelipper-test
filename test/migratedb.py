import sqlite3

con = sqlite3.connect("../database/pelipper.db")
cursor = con.cursor()
cursor.execute(
    """
    ALTER TABLE rescueaok
    ADD COLUMN rescuerpid INTEGER NOT NULL DEFAULT 0
"""
)
con.commit()
con.close()
