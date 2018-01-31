from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Paul'}
    runs = [
        {
            'runner': {'username': 'Ling'},
            'run_name': 'Run with Paul',
            'distance': 5.2
        },
        {
            'runner': {'username': 'Almond'},
            'run_name': "My paws are tired",
            'distance': 3.1
        }
    ]
    return render_template('index.html', title='Home', user=user, runs=runs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
