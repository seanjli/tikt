from index import db

class Problem(db.Model):

    __tablename__ = "aime"

    ID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    tags = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=False)
    diff = db.Column(db.Integer)
    statement = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)

    def __init__(self, title, tags, subject, diff, statement, link, answer):
        self.title = title
        self.tags = tags
        self.subject = subject
        self.diff = diff
        self.statement = statement
        self.link = link
        self.answer = answer

    def __repr__(self):
        return "<problem {0}>".format(self.title)

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    salted_pwd = db.Column(db.String, nullable=False)
    testcount = db.Column(db.Integer)
    pused = db.Column(db.String)
    pfav = db.Column(db.String)

    def __init__(self, user, email, salted_pwd):
        self.user = user
        self.email = email
        self.salted_pwd = salted_pwd
        self.testcount = 0
        self.pused = " "
        self.pfav = " "

    def __repr__(self):
        return '<User {0}>'.format(self.user)

class Test(db.Model):

    __tablename__ = 'tests'

    test_id = db.Column(db.Integer, primary_key=True)
    test_url = db.Column(db.String, unique=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    exam_type = db.Column(db.String, nullable=False)
    pnum = db.Column(db.Integer, nullable=False)
    problems = db.Column(db.String, nullable=False)

    def __init__(self, test_url, title, author, date, exam_type, pnum, problems):
        self.test_url = test_url
        self.title = title
        self.author = author
        self.date = date
        self.exam_type = exam_type
        self.pnum = pnum
        self.problems = problems
