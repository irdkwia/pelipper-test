import sqlite3

con = sqlite3.connect("../database/pelipper.db")
cursor = con.cursor()
cursor.execute(
    """
    ALTER TABLE wmpasslist
    ADD COLUMN prefix INTEGER NOT NULL DEFAULT ""
"""
)
con.commit()
con.close()
