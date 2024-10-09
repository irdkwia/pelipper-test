import sqlite3

con = sqlite3.connect("../database/pelipper.db")

cur = con.cursor()

cur.execute(
    """
    DELETE FROM wmpasslist
""",
)

con.commit()
con.close()
