from flask import render_template, send_from_directory, redirect, url_for, flash, make_response, request
from app.main import bp
from flask_login import current_user, login_required
from app.main.forms import *
from app.models import Voyage, Gare, Reduction, Place, Billet, Client
import json


@bp.route('/create_admin')
def create_admin():
    has_admin = Client.query.filter_by(admin=True).first()
    if has_admin:
        flash('Un admin existe déjà !', 'info')
    else:
        admin = Client(pseudo='admin', nom='admin', prenom='admin', age=99, argent=0, admin=True)
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        flash('Vous venez de créer un admin !', 'success')
    return redirect(url_for('edit.edit_index'))


@bp.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    return render_template('home.html', title='Bienvenue dans notre agence')


@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.admin:
        return redirect(url_for('edit.edit_index'))

    form = RechercheTrajet()

    gares = Gare.query.all()

    choix_gares = [(gare.id, '{} - {}'.format(gare.ville, gare.nom)) for gare in gares]
    choix_gares_arrivee = choix_gares[1:]

    form.gareDepart.choices = choix_gares
    form.gareArrivee.choices = choix_gares_arrivee

    reduction = Reduction.query.filter_by(id=current_user.idReduction).first()
    reduction = 0 if reduction is None else reduction.pourcentage

    if request.method == 'POST':
        form.gareArrivee.choices = choix_gares

        if form.validate_on_submit():
            voyages = Voyage.query.filter_by(idGareDepart=form.gareDepart.data, idGareArrivee=form.gareArrivee.data)
            return render_template('index.html', title='Accueil', voyages=voyages, form=form, reduction=reduction)
    return render_template('index.html', title='Accueil', form=form)


@bp.route('/gares/get_all_but/<gareId>')
def gares_get_all_butt(gareId):
    gares = Gare.query.filter(Gare.id != gareId)
    data = [(gare.id, '{} - {}'.format(gare.ville, gare.nom)) for gare in gares]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response


# Visualiser un voyage en particulier et effectuer une réservation
@bp.route('/voyages/<voyageId>', methods=['GET', 'POST'])
def voyage(voyageId):
    if current_user.admin:
        return redirect(url_for('edit.edit_index'))

    voyage = Voyage.query.filter_by(id=voyageId).first_or_404()
    gareDepart = Gare.query.filter_by(id=voyage.idGareDepart).first()
    gareArrivee = Gare.query.filter_by(id=voyage.idGareArrivee).first()

    train = Train.query.filter_by(numTrain=voyage.numTrain).first()

    voitures = train.voitures.filter_by(classe1=False).all()
    choix_voitures = [(voiture.id, '{}'.format(voiture.numVoiture)) for voiture in voitures]

    places = Place.query.filter_by(idVoiture=voitures[0].id).all()
    choix_places = [(place.id, '{}'.format(place.numPlace)) for place in places]

    form = ChoisirPlace()
    form.voiture.choices = choix_voitures
    form.place.choices = choix_places

    if request.method == 'POST':
        choix_voitures = [(voiture.id, '{}'.format(voiture.numVoiture)) for voiture in train.voitures]
        places = Place.query.filter_by(idVoiture=form.voiture.data)
        choix_places = [(place.id, '{}'.format(place.numPlace)) for place in places]
        form.voiture.choices = choix_voitures
        form.place.choices = choix_places

        if form.validate_on_submit():
            classe1 = form.classe.data == 1
            cout = voyage.prixClasse1 if classe1 else voyage.prixClasse2
            if current_user.argent < cout:
                flash('Vous n\'avez pas asser d\'argent pour acheter cet billet', 'danger')
                return redirect(url_for('main.moncompte'))
            current_user.set_argent(current_user.argent - cout)
            billet = Billet.query.filter_by(idVoyage=voyageId, idPlace=form.place.data).first()
            billet.set_idClient(current_user.id)
            db.session.commit()
            flash('Vous venez d\'acheter un billet de train', 'success')
            return redirect(url_for('main.index'))
    return render_template('voyage.html', title='Voyage', jumbotron_title='Réserver', form=form, voyage=voyage,
                           gareDepart=gareDepart, gareArrivee=gareArrivee, train=train)


@bp.route('/trains/<numTrain>/classe1')
def get_voitures_classe1(numTrain):
    if current_user.admin:
        return redirect(url_for('edit.edit_index'))

    train = Train.query.filter_by(numTrain=numTrain).first()
    voitures = train.voitures.filter_by(classe1=True)
    data = [(voiture.id, '{}'.format(voiture.numVoiture)) for voiture in voitures]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response


@bp.route('/trains/<numTrain>/classe2')
def get_voitures_classe2(numTrain):
    if current_user.admin:
        return redirect(url_for('edit.edit_index'))

    train = Train.query.filter_by(numTrain=numTrain).first()
    voitures = train.voitures.filter_by(classe1=False)
    data = [(voiture.id, '{}'.format(voiture.numVoiture)) for voiture in voitures]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response


@bp.route('/voitures/<voitureId>/places')
def get_places(voitureId):
    if current_user.admin:
        return redirect(url_for('edit.edit_index'))

    voiture = Voiture.query.filter_by(id=voitureId).first()
    data = [(place.id, '{}'.format(place.numPlace)) for place in voiture.places]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(bp.root_path, 'favicon.ico')


@bp.route('/moncompte', methods=['GET', 'POST'])
@login_required
def moncompte():
    if current_user.admin:
        return redirect(url_for('edit.edit_index'))

    form_portefeuille = RechargerArgent()
    if form_portefeuille.validate_on_submit():
        current_user.set_argent(current_user.argent + form_portefeuille.recharge.data)
        db.session.commit()
        flash('Vous avez rechargé {} sur votre compte'.format(form_portefeuille.recharge.data), 'success')
        return redirect(url_for('main.moncompte'))

    form_reduction = AcheterReduction()
    reductions = Reduction.query.all()
    choix_reductions = [(reduction.id, '{} - {} % - {} €'.format(reduction.type, reduction.pourcentage, reduction.prix))
                        for reduction in reductions if reduction.id != current_user.idReduction]
    form_reduction.reduction.choices = choix_reductions
    if form_reduction.validate_on_submit():
        carte = Reduction.query.filter_by(id=form_reduction.reduction.data).first_or_404()
        cout = carte.prix
        if current_user.argent < cout:
            flash('Vous n\'avez pas asser d\'argent pour acheter cette réduction', 'danger')
            return redirect(url_for('main.moncompte'))
        current_user.set_idReduction(form_reduction.reduction.data)
        current_user.set_argent(current_user.argent - cout)
        db.session.commit()
        flash('Vous avez acheté une carte de réduction', 'success')
        return redirect(url_for('main.moncompte'))

    reduction = Reduction.query.filter_by(id=current_user.idReduction).first()

    voyages = db.session.query(Voyage).join(Billet).filter(Billet.idClient == current_user.id).distinct().all()
    return render_template('moncompte.html', title='Mon compte', voyages=voyages, form_reduction=form_reduction,
                           form_portefeuille=form_portefeuille, reduction=reduction,
                           jumbotron_title='{}'.format(current_user.pseudo))
