from index import db
import datetime

# MANY TO MANY TABLES

favorites = db.Table('favorites',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'))
        )

usedprobs = db.Table('usedprobs',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'))
        )

taglist = db.Table('taglist',
        db.Column('problem_id', db.Integer, db.ForeignKey('problem.id')),
        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
        )

testcomp = db.Table('testcomp',
        db.Column('test_id', db.Integer, db.ForeignKey('test.id')),
        db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'))
        )

bantable = db.Table('bantable',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('contest_id', db.Integer, db.ForeignKey('contest.id'))
        )

# USER CLASS

class User(db.Model):

    # ATTRIBUTES

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, unique=True, nullable=False)
    pwd = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    role = db.Column(db.String, default="user")
    logged = db.Column(db.Integer, default=0)

    # RELATIONS

    favs = db.relationship('Problem', secondary=favorites, backref=db.backref('lovers'))
    used = db.relationship('Problem', secondary=usedprobs, backref=db.backref('users'))
    tests = db.relationship('Test', backref='user')
    banned = db.relationship('User', secondary=bantable, backref='haters')

# PROBLEM CLASS

class Problem(db.Model):
    
    # ATTRIBUTES

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=False)
    diff = db.Column(db.Integer)
    statement = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'))
    
    # RELATIONS

    tags = db.relationship('Tag', secondary=taglist, backref=db.backref('probs'))

# TAG CLASS

class Tag(db.Model):

    # ATTRIBUTES

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pop = db.Column(db.Integer, default=0)

# TEST CLASS

class Test(db.Model):

    # ATTRIBUTES

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    type = db.Column(db.String, nullable=False)
    size = db.Column(db.Integer, nullable=False)

    # RELATIONS

    probs = db.relationship('Problem', secondary=testcomp, backref=db.backref('tests'))

# CONTEST CLASS

class Contest(db.Model):

    # ATTRIBUTES

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    unpop = db.Column(db.Integer)

    # RELATIONS

    probs = db.relationship('Problem', backref='contest')
