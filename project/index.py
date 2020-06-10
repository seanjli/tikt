import sqlite3
from functools import wraps

from flask import Flask, flash, redirect, render_template, \
        request, session, url_for

from forms import TestForm
import gen_test

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('_config')

@app.route('/', methods=['GET', 'POST'])
def generate():
    form = TestForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            key = gen_test.make_test(form.name.data, form.prob_num.data)
            flash("Success! Click below to download your test.")
            return redirect(url_for('test', test_id = key))
        else:
            flash("Sorry, something went wrong.")
            return render_template('index.html',
                    form = form)
    
    return render_template('index.html',
        form = form)

@app.route('/success/<test_id>')
def test(test_id):
    return render_template(
            'test.html',test_url = url_for("static", filename="tests/"+test_id+".pdf"))
