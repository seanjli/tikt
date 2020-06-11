# project/index.py
# controls entire website

#################
#### imports ####
#################

import sqlite3
from functools import wraps

from flask import Flask, flash, redirect, render_template, \
        request, session, url_for

from forms import TestForm, LoginForm
import gen_test

from flask_sqlalchemy import SQLAlchemy

################
#### config ####
################

app = Flask(__name__)
app.config.from_object('_config')

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
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.user.data != app.config['USERNAME'] \
                    or form.pwd.data != app.config['PASSWORD']:
                error = 'Invalid Credentials. Please try again.'
                return render_template('login.html', error=error)
            else:
                session['logged_in'] = True
                flash('Welcome!')
                return redirect(url_for('generate'))
    return render_template('login.html', form=form)

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
