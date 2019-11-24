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

    billets = db.relationship('Billet', backref='client', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def check_password(self, password):
        return check_password_hash(pwhash=self.password_hash, password=password)


class Train(db.Model):
    numTrain = db.Column(db.Integer, primary_key=True)

    voitures = db.relationship('Voiture', backref='train', lazy='dynamic', cascade="all, delete, delete-orphan")
    voyages = db.relationship('Voyage', backref='train', lazy='dynamic')

    def __repr__(self):
        return '<Train {}>'.format(self.numTrain)


class Voiture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numVoiture = db.Column(db.Integer)
    numTrain = db.Column(db.Integer, db.ForeignKey('train.numTrain'))

    places = db.relationship('Place', backref='voiture', lazy='dynamic', cascade="all, delete, delete-orphan")

    def __repr__(self):
        return '<Voiture {}>'.format(self.id)


class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numPlace = db.Column(db.Integer)
    idVoiture = db.Column(db.Integer, db.ForeignKey('voiture.id'))

    billets = db.relationship('Billet', backref='place', lazy='dynamic', cascade="all, delete, delete-orphan")


class Gare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ville = db.Column(db.String(64))
    nom = db.Column(db.String(64))

    departs = db.relationship('Voyage', backref='gareDepart', lazy='dynamic', foreign_keys='Voyage.idGareDepart',
                              cascade="all, delete, delete-orphan")
    arrivees = db.relationship('Voyage', backref='gareArrivee', lazy='dynamic', foreign_keys='Voyage.idGareArrivee',
                               cascade="all, delete, delete-orphan")

    def __repr__(self):
        return '<Gare {} - {}>'.format(self.ville, self.nom)


class Voyage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    horaireDepart = db.Column(db.DateTime, index=True)
    horaireArrivee = db.Column(db.DateTime, index=True)
    idGareDepart = db.Column(db.Integer, db.ForeignKey('gare.id'))
    idGareArrivee = db.Column(db.Integer, db.ForeignKey('gare.id'))
    numTrain = db.Column(db.Integer, db.ForeignKey('train.numTrain'))

    billets = db.relationship('Billet', backref='voyage', lazy='dynamic', cascade="all, delete, delete-orphan")

    def __repr__(self):
        return '<Voyage {}>'.format(self.id)


class Billet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prix = db.Column(db.Integer, default=30)
    idVoyage = db.Column(db.Integer, db.ForeignKey('voyage.id'))
    idPlace = db.Column(db.Integer, db.ForeignKey('place.id'))
    idClient = db.Column(db.Integer, db.ForeignKey('client.id'))
