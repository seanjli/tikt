import sqlite3
from _config import DATABASE

with sqlite3.connect(DATABASE) as conn:
    c = conn.cursor()
    c.execute(
            """CREATE TABLE users(user TEXT, email TEXT, pwd TEXT, salt TEXT)"""
            )
