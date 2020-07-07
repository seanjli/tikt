from index import db
from models import Problem, User, Test
from datetime import date
from _config import DATABASE

import csv
import sqlite3

db.create_all()
db.session.commit()
