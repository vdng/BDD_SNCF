from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import Train, Voiture, Gare
from app import db
from datetime import datetime


class AddTrainForm(FlaskForm):
    nbVoitures = IntegerField("Nombre de voitures", default=3, validators=[DataRequired()])
    nbPlacesParVoiture = IntegerField("Capacité par voiture", default=10, validators=[DataRequired()])
    submit = SubmitField("Ajouter un train")


class AddVoitureForm(FlaskForm):
    capacite = IntegerField("Capacité", default=16, validators=[DataRequired()])
    submit = SubmitField("Ajouter une voiture")


class AddGareForm(FlaskForm):
    ville = StringField("Ville", validators=[DataRequired()])
    nom = StringField("Nom de la gare", validators=[DataRequired()])
    submit = SubmitField("Ajouter une gare")


class AddVoyageForm(FlaskForm):
    gareDepart = SelectField("Gare de départ", coerce=int, validators=[DataRequired()])
    gareArrivee = SelectField("Gare d'arrivée", coerce=int, validators=[DataRequired()])
    horaireDepart = DateTimeField("Horaire de départ", default=datetime.utcnow, validators=[DataRequired()])
    horaireArrivee = DateTimeField("Horaire d'arrivée", default=datetime.utcnow, validators=[DataRequired()])
    train = SelectField("Effectué par", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Ajouter un voyage")


class AddReductionForm(FlaskForm):
    type = StringField("Type réduction", validators=[DataRequired()])
    pourcentage = IntegerField("%", validators=[DataRequired()])
    prix = IntegerField("Coût", validators=[DataRequired()])
    submit = SubmitField("Ajouter une carte de réduction")

    def validate_pourcentage(self, pourcentage):
        if not 0 < pourcentage.data < 100:
            raise ValidationError("Le pourcentage de réduction doit être strictement compris entre 0% et 100%")
