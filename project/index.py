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

@app.route('/home', methods=['GET', 'POST'])
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
        return render_template('denied.html')
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
