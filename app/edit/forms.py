from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import Train, Voiture


class AddTrainForm(FlaskForm):
    submit = SubmitField("Ajouter un train")
