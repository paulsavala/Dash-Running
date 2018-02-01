from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User

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
            'run_name': 'My paws are tired',
            'distance': 3.1
        }
    ]
    return render_template('index.html', title='Home', user=user, runs=runs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
