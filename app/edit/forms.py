from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import Train, Voiture, Gare
from app import db
from datetime import datetime


class AddTrainForm(FlaskForm):
    nbVoitures = IntegerField("Nombre de voitures", default=3,
                              validators=[DataRequired(message="Le nombre de voitures est un nombre")])
    nbPlacesParVoiture = IntegerField("Capacité par voiture", default=10,
                                      validators=[DataRequired(message="Veuillez indiquer un nombre de places valide")])
    nbVoituresClasse1 = IntegerField("Nombre de voitures 1ere classe",
                                     validators=[DataRequired(message="Veuillez indiquer un nombre valide")], default=1)
    submit = SubmitField("Ajouter un train")

    def validate_nbVoituresClasse1(self, nbVoituresClasse1):
        if self.nbVoitures.data < nbVoituresClasse1.data:
            raise ValidationError("Le nombre de voitures 1ere classe ne doit pas dépasser le nombre de voitures total")

    def validate_nbVoitures(self, nbVoitures):
        if not 0 < nbVoitures.data < 21:
            raise ValidationError("Le nombre de voitures doit être compris entre 1 et 20")

    def validate_nbPlacesParVoiture(self, nbPlacesParVoiture):
        if not 2 < nbPlacesParVoiture.data < 51:
            raise ValidationError("Une voiture ne peut avoir moins de 2 places et plus de 50 places")


class AddVoitureForm(FlaskForm):
    capacite = IntegerField("Capacité", default=16,
                            validators=[DataRequired(message="La capacité doit être un nombre")])
    classe1 = BooleanField("1ere classe")
    submit = SubmitField("Ajouter une voiture")

    def validate_capacite(self, capacite):
        if not 2 < capacite.data < 51:
            raise ValidationError("Une voiture ne peut avoir moins de 2 places et plus de 50 places")


class AddGareForm(FlaskForm):
    ville = StringField("Ville", validators=[DataRequired(message="Veuillez préciser le nom de la ville")])
    nom = StringField("Nom de la gare", validators=[DataRequired(message="Veuillez préciser le nom de la gare")])
    submit = SubmitField("Ajouter une gare")


class AddVoyageForm(FlaskForm):
    gareDepart = SelectField("Gare de départ", coerce=int, validators=[DataRequired()])
    gareArrivee = SelectField("Gare d'arrivée", coerce=int, validators=[DataRequired()])
    horaireDepart = DateTimeField("Horaire de départ", default=datetime.utcnow, validators=[DataRequired()])
    horaireArrivee = DateTimeField("Horaire d'arrivée", default=datetime.utcnow, validators=[DataRequired()])
    train = SelectField("Effectué par", coerce=int, validators=[DataRequired()])
    prixClasse1 = IntegerField("Prix 1ere classe", validators=[DataRequired(message="Le prix doit être un nombre")],
                               default=50)
    prixClasse2 = IntegerField("Prix 2nde classe", validators=[DataRequired(message="Le prix doit être un nombre")],
                               default=30)
    submit = SubmitField("Ajouter un voyage")

    def validate_prixClasse2(self, prixClasse2):
        if self.prixClasse1.data < prixClasse2.data:
            raise ValidationError("La 1ere classe doit être plus chère que la 2nde")

    def validate_horaireArrivee(self, horaireArrivee):
        if horaireArrivee.data < self.horaireDepart.data:
            raise ValidationError("Le train ne peut pas arriver avant son départ")
        elif horaireArrivee.data == self.horaireDepart.data:
            raise ValidationError("Le train ne peut pas arriver en même temps que départ")

    def validate_gareArrivee(self, gareArrivee):
        if gareArrivee.data == self.gareDepart.data:
            raise ValidationError("La gare d'arrivée ne peut pas être la même que la gare de départ")


class AddReductionForm(FlaskForm):
    type = StringField("Type réduction", validators=[DataRequired(message="Il faut un type de réduction")])
    pourcentage = IntegerField("%", validators=[DataRequired(message="Le pourcentage doit être un nombre")])
    prix = IntegerField("Coût", validators=[DataRequired(message="Le prix doit être un nombre")])
    submit = SubmitField("Ajouter une carte de réduction")

    def validate_pourcentage(self, pourcentage):
        if not 0 < pourcentage.data < 100:
            raise ValidationError("Le pourcentage de réduction doit être strictement compris entre 0% et 100%")
