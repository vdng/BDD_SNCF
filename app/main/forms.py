from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import Train, Voiture, Gare
from app import db
from datetime import datetime


class RechercheTrajet(FlaskForm):
    gareDepart = SelectField("Gare de départ", coerce=int)
    gareArrivee = SelectField("Gare d'arrivée", coerce=int)
    submit = SubmitField("Rechercher")
