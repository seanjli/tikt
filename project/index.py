# project/index.py
# controls entire website

#################
#### imports ####
#################

import sqlite3
import bcrypt
from functools import wraps

from flask import Flask, flash, redirect, render_template, \
        request, session, url_for, g

from forms import TestForm, LoginForm, RegisterForm
import gen_test

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError

################
#### config ####
################

app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Problem, User, Test

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

# route handlers

@app.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('Goodbye!')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
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
                    flash('Welcome!')
                    return redirect(url_for('generate'))
        else:
            error = 'Both fields are required.'
        if form.validate_on_submit():
            if request.form['user'] == 'admin' and request.form['pwd'] == 'admin':
                session['logged_in'] = True
                flash('Welcome!')
                return redirect(url_for('generate'))
            else:
                error = "Invalid username or password."

    return render_template('login.html', form=form, error = error)

@app.route('/home', methods=['GET', 'POST'])
@login_required
def generate():
    form = TestForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            key = gen_test.make_test(form.name.data, form.author.data, form.prob_num.data, form.min_diff.data, form.max_diff.data)
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
