from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, select

from models import Problem, Test, Tag, Contest
from index import db

def seg(a,b,t):
    return (1-t)*a + t*b

def make_test(size, a, b, tags):

    problems = []

    valid = db.session.query(Problem).filter(Problem.diff >= a).filter(Problem.diff <= b).order_by(func.random())

    part1 = valid.filter(Problem.diff <= seg(a,b,0.3)).all()
    part2 = valid.filter(Problem.diff > seg(a,b,0.3)).filter(Problem.diff <= seg(a,b,0.5)).all()
    part3 = valid.filter(Problem.diff > seg(a,b,0.5)).filter(Problem.diff <= seg(a,b,0.75)).all()
    part4 = valid.filter(Problem.diff > seg(a,b,0.75)).all()

    if tags and len(tags) > 0:
        part1 = [p for p in part1 if set(tags).issubset(set([t.id for t in p.tags]))]
        part2 = [p for p in part2 if set(tags).issubset(set([t.id for t in p.tags]))]
        part3 = [p for p in part3 if set(tags).issubset(set([t.id for t in p.tags]))]
        part4 = [p for p in part4 if set(tags).issubset(set([t.id for t in p.tags]))]
    
    if len(part1) + len(part2) + len(part3) + len(part4) < size:
        return "fail"
    
    i = 0

    while len(problems) < size:
        if i < len(part1):
            problems.append(part1[i])
        if i < len(part2):
            problems.append(part2[i])
        if i < len(part3):
            problems.append(part3[i])
        if i < len(part4):
            problems.append(part4[i])
        i += 1

    problems = problems[:size]

    problems.sort(key=lambda x: x.diff)
    difflist = [p.diff for p in problems]

    return problems
