#Admin Login Page
import sqlite3

import hashlib

conn = sqlite3.connect("userdata.db")

cur = conn.cursor()


cur.execute("""

CREATE TABLE IF NOT EXISTS userdata (
    id INTEGER PRIMARY KEY,
    username varchar(255) NOT NULL,
    password VARCHAR(255) NOT NULL
)
""")     