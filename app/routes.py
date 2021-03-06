from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Run
from werkzeug.urls import url_parse
from werkzeug import secure_filename
import os
from app.fileIO import allowed_file, metadata_from_gpx, gpx_to_csv_to_msm

@app.route('/')
@app.route('/index')
@login_required
def index():
    runs = Run.query.filter_by(user_id=current_user.id)
    return render_template('index.html', title='Home', runs=runs)

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
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome to Dash Running.')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nothing to upload')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Please select a GPX file to upload')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name, date, time = metadata_from_gpx(filename)
            run = Run.query.filter_by(name=name, date=date, time=time, \
                                        user_id=current_user.id)
            if run.first() is not None:
                flash('This run already exists in the database')
                return redirect(request.url)
            run = Run(name=name, date=date, time=time, user_id=current_user.id)
            distance, elevation_gain = gpx_to_csv_to_msm(run, filename)
            # Distance and elevation_gain do not yet work
            run.distance = distance
            run.elevation_gain = elevation_gain
            db.session.add(run)
            db.session.commit()
            flash(name + ' successfully uploaded and processed.')
            return redirect(url_for('index'))
    return render_template('upload.html', title='Upload')

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    runs = Run.query.filter_by(user_id=user.id)
    return render_template('user.html', user=user, runs=runs)
