# project/index.py
# controls entire website

#################
#### imports ####
#################

import sqlite3
import datetime
import bcrypt
import os
from functools import wraps

from flask import Flask, flash, redirect, render_template, \
        request, session, url_for, g

from forms import TestForm, LoginForm, RegisterForm
import test_gen, test_render

from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import secure_filename

from sqlalchemy.exc import IntegrityError

################
#### config ####
################

app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = ['csv']

from models import Problem, User, Test
from db_addproblems import update_problems

##############
#### meat ####
##############

# helper functions

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_tests():
    return db.session.query(Test).filter_by(author=session['user_id']).order_by(Test.date.asc())

def get_user():
    return (db.session.query(User).filter_by(user_id=str(session['user_id'])))[0]

def get_probs(prob_ids):
    probs = []
    for pid in prob_ids:
        prob = (db.session.query(Problem).filter_by(ID = pid))[0]
        probs.append(prob)
    return probs

def get_fav_ids():
    user = get_user()
    favs = user.pfav.split(",")
    if favs == [""]:
        favs = []
    return favs

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# route handlers

@app.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Goodbye!')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if 'logged_in' in session:
        return redirect(url_for('generate'))
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(user=request.form['user']).first()
            if user is None:
                error = "Invalid username or passsword."
            else:
                pwd = request.form['pwd']
                if not bcrypt.checkpw(pwd.encode('utf8'), user.salted_pwd):
                    error = 'Invalid username or password.'
                    return render_template('login.html', form=form, error=error)
                else:
                    session['logged_in'] = True
                    session['user_id'] = user.user_id
                    session['role'] = user.role
                    flash('Welcome!')
                    return redirect(url_for('generate'))
        else:
            error = 'Both fields are required.'

    return render_template('login.html', form=form, error = error)

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    form = TestForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            problems = test_gen.make_test(form.prob_num.data, form.min_diff.data, form.max_diff.data)
            key = test_render.render_test(form.name.data, form.author.data, problems)
            pids = ','.join([str(p.prob_id) for p in problems])
            new_test = Test(
                    key,
                    form.name.data,
                    session['user_id'],
                    datetime.datetime.now(),
                    'normal',
                    form.prob_num.data,
                    pids)
            db.session.add(new_test)
            db.session.commit()
            flash("Success! Click below to download your test.")
            return redirect(url_for('test', test_id = key))
        else:
            flash("Sorry, something went wrong.")
            return render_template('index.html',
                    form = form)
    
    return render_template('index.html',
        form = form)

@app.route('/success/<test_id>')
@login_required
def test(test_id):
    return render_template(
            'test.html',test_url = url_for("static", filename="tests/"+test_id+".pdf"))

@app.route('/register/', methods=['GET','POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            salt = bcrypt.gensalt()
            hash_pwd = bcrypt.hashpw(request.form['pwd'].encode('utf8'), salt)
            new_user = User(
                    form.user.data,
                    form.email.data,
                    hash_pwd)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Thanks for registering. Please login.')
                return redirect(url_for('login'))
            except IntegrityError:
                error = 'That username and/or email already exists.'
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)

@app.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload_file():
    if not session['role'] == 'admin':
        return render_template('403.html'), 403
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return render_template('upload.html')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return render_template('upload.html')
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
            update_problems(file.filename)
            flash('File upload successful')
            return redirect(url_for('generate'))
        else:
            flash('Bad file type')
            return render_template('upload.html')
    return render_template('upload.html')

@app.route('/view/')
@login_required
def view_tests():
    favs = get_fav_ids()
    probs = get_probs(favs)

    return render_template('view.html',
            tests=get_tests(),
            probs=probs
            )

@app.route('/test_info/<test_id>')
@login_required
def view_test_info(test_id):
    tests = db.session.query(Test).filter_by(test_url=test_id).order_by(Test.date.asc())
    if len(tests.all()) == 0:
        return render_template('404.html'), 404
    test = tests[0]
    if not int(test.author) == session['user_id']:
        return render_template('403.html'), 403
    prob_ids = test.problems.split(",")
    probs = get_probs(prob_ids)
    
    favs = get_fav_ids()
    hearts = []
    for pid in prob_ids:
        if pid in favs:
            hearts.append('♥')
        else:
            hearts.append('♡')

    return render_template('info.html',
            probs=probs,
            test=test,
            hearts=hearts)

@app.route('/favorite/<test_id>/<pid>')
@login_required
def favorite_problem(test_id, pid):
    user = get_user()
    favs = get_fav_ids()

    if (test_id == "UNIV"):
        if (pid in favs):
            favs.remove(pid)
            pfav_output = ""
            for i in favs:
                pfav_output = pfav_output + str(i) + ","
            pfav_output = pfav_output[:len(pfav_output)-1]
            get_user().pfav = pfav_output
            db.session.commit()
            flash("Problem with id " + pid + " successfully unfavorited.")
            return redirect(url_for('view_tests'))
        else:
            return render_template("404.html"), 404

    tests = db.session.query(Test).filter_by(test_url=test_id).order_by(Test.date.asc())
    if len(tests.all()) == 0:
        return render_template('404.html'), 404
    test = tests[0]
    if not int(test.author) == session['user_id']:
        return render_template('403.html'), 403
    prob_ids = test.problems.split(",")
    if pid not in prob_ids:
        return render_template('404.html'), 404
    favs = get_fav_ids()
    rem_state = 1
    if pid in favs:
        favs.remove(pid)
    else:
        favs.append(pid)
        rem_state = 0
    pfav_output = ""
    for i in favs:
        pfav_output = pfav_output + str(i) + ","
    pfav_output = pfav_output[:len(pfav_output)-1]
    get_user().pfav = pfav_output
    db.session.commit()
    if rem_state == 0:
        flash("Problem with id " + pid + " successfully  favorited.")
    else:
        flash("Problem with id " + pid + " successfully unfavorited.")
    return redirect(url_for("view_test_info", test_id=test_id))

