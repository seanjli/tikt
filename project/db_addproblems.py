from index import db
from models import * 
from datetime import date

import csv
import sqlite3

def update_problems(filename):
    problems = csv.reader(open("appdata/"+filename,"rU"))
    tagstuff = db.session.query(Tag)

    for row in problems:
        tags = row[7].split(',')

        problem = Problem(
                contest_id = row[0],
                title = row[1],
                subject = row[2],
                diff = int(row[3]),
                statement = row[4],
                link = row[5],
                answer = row[6]
                )

        for tag in tags:
            checktag = tagstuff.filter_by(name = tag)
            if checktag.count() == 0:
                newtag = Tag(name=tag)
                db.session.add(newtag)
            else:
                newtag = checktag.first()
            problem.tags.append(newtag)

        db.session.add(problem)
    
    db.session.commit()
