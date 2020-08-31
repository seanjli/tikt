# project/index.py
# controls entire website

#################
#### imports ####
#################

import sqlite3
import datetime
import bcrypt
import os
import json

from functools import wraps

from flask import Flask, flash, redirect, render_template, \
        request, session, url_for, g, jsonify

from forms import TestForm, LoginForm, RegisterForm

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

from models import Problem, User, Test, Tag, Contest
from db_addproblems import update_problems

from test_gen import make_test
import test_render

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

def get_user():
    user = db.session.query(User).filter_by(id=session['user_id']).first()
    db.session.commit()
    return user

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
                if not bcrypt.checkpw(pwd.encode('utf8'), user.pwd):
                    error = 'Invalid username or password.'
                    return render_template('login.html', form=form, error=error)
                else:
                    session['logged_in'] = True
                    session['user_id'] = user.id
                    session['role'] = user.role
                    flash('Welcome!')
                    return redirect(url_for('generate'))
        else:
            error = 'Both fields are required.'

    return render_template('login.html', form=form, error=error)

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
   
    user = get_user()
    form = TestForm()

    all_tags = db.session.query(Tag).all()

    choices = []

    for tag in all_tags:
        if len(tag.probs) >= 15:
            choices.append((tag.id, tag.name+" ("+str(len(tag.probs))+")"))

    choices.sort(key=lambda x:int(x[1].split(" (")[1][:-1]), reverse=True)

    # print(choices)

    form.tags.choices = choices


    if request.method == 'POST':
        if form.validate_on_submit():
            problems = make_test(form.prob_num.data, 
                    form.min_diff.data, 
                    form.max_diff.data,
                    form.tags.data)
            if problems == 'fail':
                error = 'Test conditions cannot be satisfied. Please loosen them.'
                return render_template('index.html', form=form, error=error)

            key = test_render.render_test(form.name.data, form.author.data, problems)
            new_test = Test(
                    url = key,
                    title = form.name.data,
                    user_id = session['user_id'],
                    type = 'normal',
                    size = form.prob_num.data
                    )

            # print([p.id for p in problems])
            # print(new_test.probs)

            for p in problems:
                new_test.probs.append(p)
                if p not in user.used:
                    user.used.append(p)
            
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
                    user = form.user.data,
                    email = form.email.data,
                    pwd = hash_pwd)
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
    return render_template('view.html',
            tests=get_user().tests,
            probs=get_user().favs
            )

@app.route('/favorite/add/<test_url>/<prob_id>')
@login_required
def favorite_problem(test_url, prob_id):
    user = get_user()

    tests = db.session.query(Test).filter_by(url=test_url)
    prob = db.session.query(Problem).filter_by(id=prob_id).first()

    if tests.count() == 0:
        return render_template('404.html'), 404
    test = tests.first()
    if not user.id == test.user_id:
        return render_template('403.html'), 403
    if not int(prob_id) in [p.id for p in test.probs]:
        return render_template('404.html'), 404
    if prob in user.favs:
        return render_template('404.html'), 404

    user.favs.append(prob)
    db.session.commit()

    flash("Problem with id " + prob_id + " successfully favorited.")

    return redirect(url_for('view_test_info', test_id=test_url))

@app.route('/favorite/remove/<test_url>/<prob_id>')
@login_required
def unfavorite_problem(test_url, prob_id):
    user = get_user()

    prob = db.session.query(Problem).filter_by(id=prob_id).first()

    if not test_url == "UNIV":
        tests = db.session.query(Test).filter_by(url=test_url)
        if tests.count() == 0:
            return render_template('404.html'), 404
        test = tests.first()
        if not user.id == test.user_id:
            return render_template('403.html'), 403
        if not int(prob_id) in [p.id for p in test.probs]:
            return render_template('404.html'), 404
    
    if not prob in user.favs:
        return render_template('404.html'), 404

    user.favs.remove(prob)
    db.session.commit()

    flash("Problem with id " + prob_id + " successfully unfavorited.")

    if not test_url == "UNIV":
        return redirect(url_for('view_test_info', test_id=test_url))
    return redirect(url_for('view_tests'))

@app.route('/test_info/<test_id>')
@login_required
def view_test_info(test_id):
    
    tests = db.session.query(Test).filter_by(url=test_id).order_by(Test.date.asc())
    if tests.count() == 0:
        return render_template('404.html'), 404
    test = tests.first()
    if not int(test.user_id) == session['user_id']:
        return render_template('403.html'), 403
    
    user = get_user()
   
    probs = test.probs
    print([p.id for p in probs])
    favids = [p.id for p in user.favs]
    hearts = []

    for prob in probs:
        if prob.id in favids:
            hearts.append('f')
        else:
            hearts.append('nf')

    return render_template('info.html',
            probs=probs,
            test=test,
            hearts=hearts)

"""
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
"""
