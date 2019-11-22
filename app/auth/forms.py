from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import Client


class LoginForm(FlaskForm):
    pseudo = StringField('Pseudo', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')


class RegistrationForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    prenom = StringField('Prenom', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    pseudo = StringField('Pseudo', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    password2 = PasswordField('Confirmation du mot de masse',
                              validators=[DataRequired(),
                                          EqualTo('password',
                                                  message='Le mot de passe et sa confirmation sont différents')])
    submit = SubmitField('Enregistrer')

    def validate_pseudo(self, pseudo):
        user = Client.query.filter_by(pseudo=pseudo.data).first()
        if user is not None:
            raise ValidationError('Pseudo déjà pris, veuillez en choisir un autre')
