import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'HEROKU_POSTGRESQL_MAUVE_URL') or 'mysql+pymysql://root:mdp@127.0.0.1:3306/sncf'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
