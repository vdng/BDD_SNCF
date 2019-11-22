from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import Train, Voiture


class AddTrainForm(FlaskForm):
    nbVoitures = IntegerField("Nombre de voitures", default=5)
    nbPlacesParVoiture = IntegerField("Capacité par voiture", default=50)
    submit = SubmitField("Ajouter un train")


class AddVoitureForm(FlaskForm):
    capacite = IntegerField("Capacité", default=50)
    submit = SubmitField("Ajouter une voiture")
