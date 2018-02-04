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
    UPLOAD_FOLDER = r'data/gpx/'
    ALLOWED_EXTENSIONS = set(['gpx'])

    # File processing settings
    GPX_FOLDER = UPLOAD_FOLDER
    CSV_FOLDER = r'data/csv/'
    MSM_FOLDER = r'data/msm/'
    # data_directories = {'root': r'data/',
    #                     'gpx': r'data/gpx/',
    #                     'csv': r'data/csv/',
    #                     'msm': r'data/max_speed_matrices/'}

    max_minutes = 120
    min_gradient = -30
    max_gradient = 30
