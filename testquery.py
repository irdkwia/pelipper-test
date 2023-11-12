import sqlite3

con = sqlite3.connect("database/pelipper.db")

cur = con.cursor()

cur.execute("""
    SELECT * FROM teamdata WHERE pid IN (1973481408,1926876140) ORDER BY udate DESC LIMIT 16
""")

print(list(map(lambda x: x[0], cur.description)))
print(cur.fetchall())
con.close()
