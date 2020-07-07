from index import db
from models import Problem, User, Test
from datetime import date
from _config import DATABASE

import csv
import sqlite3

def update_problems(filename):
    problems = csv.reader(open("appdata/"+filename,"rU"))
    for row in problems:
        db.session.add(Problem(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

    db.session.commit()
