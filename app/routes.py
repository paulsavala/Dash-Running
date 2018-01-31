from flask import render_template
from app import app

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
            'run_name': "I don't like hills",
            'distance': 3.1
        }
    ]
    return render_template('index.html', title='Home', user=user, runs=runs)
