from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Pseudo', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')


class RegistrationForm(FlaskForm):
    username = StringField('Pseudo', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    password2 = PasswordField('Confirmation du mot de masse',
                              validators=[DataRequired(),
                                          EqualTo('password',
                                                  message='Le mot de passe et sa confirmation sont différents')])
    submit = SubmitField('Enregistrer')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Pseudo déjà pris, veuillez en choisir un autre')
