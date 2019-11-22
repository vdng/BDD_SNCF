from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return Client.query.get(int(id))


class Client(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    nom = db.Column(db.String(64))
    prenom = db.Column(db.String(64))
    age = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def check_password(self, password):
        return check_password_hash(pwhash=self.password_hash, password=password)


class Train(db.Model):
    numTrain = db.Column(db.Integer, primary_key=True)
    voitures = db.relationship('Voiture', backref='train', lazy='dynamic')

    def __repr__(self):
        return '<Train {}>'.format(self.numTrain)


class Voiture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numVoiture = db.Column(db.Integer)
    nbPlaces = db.Column(db.Integer)
    numTrain = db.Column(db.Integer, db.ForeignKey('train.numTrain'))

    def __repr__(self):
        return '<Voiture {}>'.format(self.id)
