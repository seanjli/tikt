from index import db
from models import *

def add_contest(name):
    db.session.add(Contest(name=name))
    db.session.commit()
