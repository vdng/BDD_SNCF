from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import Train, Voiture, Gare
from app import db
from datetime import datetime


class AddTrainForm(FlaskForm):
    nbVoitures = IntegerField("Nombre de voitures", default=5)
    nbPlacesParVoiture = IntegerField("Capacité par voiture", default=50)
    submit = SubmitField("Ajouter un train")


class AddVoitureForm(FlaskForm):
    capacite = IntegerField("Capacité", default=50)
    submit = SubmitField("Ajouter une voiture")


class AddGareForm(FlaskForm):
    ville = StringField("Ville")
    nom = StringField("Nom de la gare")
    submit = SubmitField("Ajouter une gare")


class AddVoyageForm(FlaskForm):
    gareDepart = SelectField("Gare de départ", coerce=int)
    gareArrivee = SelectField("Gare d'arrivée", coerce=int)
    horaireDepart = DateTimeField("Horaire de départ", default= datetime.utcnow)
    horaireArrivee = DateTimeField("Horaire d'arrivée", default= datetime.utcnow)
    train = SelectField("Effectué par", coerce=int)
    submit = SubmitField("Ajouter un voyage")
