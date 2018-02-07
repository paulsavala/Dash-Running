import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Flask secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # SQL Alchemy parameters
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload settings
    ALLOWED_EXTENSIONS = set(['gpx'])
    UPLOAD_FOLDER = r'data/gpx/'
    GPX_FOLDER = UPLOAD_FOLDER
    CSV_FOLDER = r'data/csv/'
    MSM_FOLDER = r'data/msm/'

    # File processing settings
    MAX_MINUTES = 120 #120
    MIN_GRADIENT = -30
    MAX_GRADIENT = 30
