from flask import render_template, flash, redirect, url_for, request, current_app, make_response
from flask_login import current_user, login_required
import json
from app import db
from app.edit import bp
from app.models import *
from app.edit.forms import *
from sqlalchemy import or_, and_, not_


@bp.route('/')
@login_required
def edit_index():
    if current_user.admin:
        return render_template('edit/edit_index.html', title='Page administrateur')
    return redirect(url_for('main.index'))


# TRAINS
# ======

# Lister tous les trains, et possibilité de rajouter ou supprimer des trains
@bp.route('/trains', methods=['GET', 'POST'])
@login_required
def trains():
    if not current_user.admin:
        return redirect(url_for('main.index'))

    form = AddTrainForm()
    if form.validate_on_submit():
        train = Train()
        db.session.add(train)
        for i in range(form.nbVoitures.data):
            classe1 = True if i < form.nbVoituresClasse1.data else False
            voiture = Voiture(numVoiture=i + 1, train=train, classe1=classe1)
            for j in range(form.nbPlacesParVoiture.data):
                place = Place(numPlace=j + 1, voiture=voiture)
                db.session.add(place)
            db.session.add(voiture)
        db.session.commit()
        flash('Nouveau train créé', 'success')
        flash(f'Train n°{train.numTrain}, avec {form.nbVoitures.data} voitures '
              f'(nb 1ere classe : {form.nbVoituresClasse1.data}), '
              f'{form.nbPlacesParVoiture.data} places par voiture', 'info')
        return redirect(url_for('edit.trains'))

    trains_capacite = db.session.query(Train.numTrain, db.func.count(Place.id).label("capacite")
                                       ).join(Voiture, Train.numTrain == Voiture.numTrain
                                              ).join(Place, Voiture.id == Place.idVoiture
                                                     ).group_by(Train.numTrain).cte(name="trains_capacite")

    trains_nbVoitures = db.session.query(trains_capacite.c.numTrain, trains_capacite.c.capacite,
                                         db.func.count(Voiture.id).label("nbVoitures")
                                         ).join(Voiture, trains_capacite.c.numTrain == Voiture.numTrain
                                                ).group_by(trains_capacite.c.numTrain).cte(name="trains_nbVoitures")

    trains = db.session.query(trains_nbVoitures.c.numTrain, trains_nbVoitures.c.capacite,
                              trains_nbVoitures.c.nbVoitures,
                              db.func.count(Voiture.id).label("nbClasse1")
                              ).outerjoin(Voiture, trains_nbVoitures.c.numTrain == Voiture.numTrain
                                          ).filter(Voiture.classe1 == True).group_by(trains_nbVoitures.c.numTrain)

    return render_template('edit/trains.html', title='Trains', trains=trains.all(), form=form)


# Visualiser un train en particulier, possibilité de rajouter et supprimer des voitures
@bp.route('/trains/<numTrain>', methods=['GET', 'POST'])
@login_required
def edit_train(numTrain):
    if not current_user.admin:
        return redirect(url_for('main.index'))

    train = Train.query.filter_by(numTrain=numTrain).first_or_404()
    voitures = train.voitures.order_by(Voiture.numVoiture)
    numTotVoitures = voitures.count()

    voyages = Voyage.query.filter_by(numTrain=numTrain).all()

    # Ajouter une voiture
    form = AddVoitureForm()
    if form.validate_on_submit():
        numVoiture = 1
        while numVoiture <= numTotVoitures and numVoiture == voitures[numVoiture - 1].numVoiture:
            numVoiture += 1
        voiture = Voiture(numVoiture=numVoiture, train=train, classe1=form.classe1.data)
        db.session.add(voiture)
        for j in range(form.capacite.data):
            place = Place(numPlace=j + 1, voiture=voiture)
            db.session.add(place)
            for voyage in voyages:
                billet = Billet(voyage=voyage, place=place)
                db.session.add(billet)
        db.session.commit()
        flash('Voiture ajoutée', 'success')
        flash(f'Voiture id: {voiture.id}, capacité: {form.capacite.data}, 1re classe: {form.classe1.data}', 'info')
        return redirect(url_for('edit.edit_train', numTrain=numTrain))

    voitures = train.voitures.order_by(Voiture.numVoiture)
    return render_template('edit/train.html', title='Edit Train', jumbotron_title='Train n°{}'.format(train.numTrain),
                           train=train, voitures=voitures, form=form)


# Supprimer un train
@bp.route('/trains/delete/<numTrain>')
@login_required
def delete_train(numTrain):
    if not current_user.admin:
        return redirect(url_for('main.index'))

    train = Train.query.filter_by(numTrain=numTrain).first()
    if train is None:
        flash('Le train n°{} n\'existe pas.'.format(numTrain), 'danger')
        return redirect(url_for('edit.trains'))
    db.session.delete(train)
    db.session.commit()
    flash('Le train n°{} a bien été supprimé.'.format(numTrain), 'success')
    return redirect(url_for('edit.trains'))


# Supprimer une voiture
@bp.route('/trains/<numTrain>/delete/<idVoiture>')
@login_required
def delete_voiture(numTrain, idVoiture):
    if not current_user.admin:
        return redirect(url_for('main.index'))

    voiture = Voiture.query.filter_by(id=idVoiture).first()
    if voiture is None:
        flash('La voiture d\'id {} n\'existe pas.'.format(idVoiture), 'danger')
        return redirect(url_for('edit.voitures'))
    db.session.delete(voiture)
    db.session.commit()
    flash('La voiture n°{} a bien été supprimée.'.format(voiture.numVoiture), 'success')
    return redirect(url_for('edit.edit_train', numTrain=numTrain))


# GARES
# =====

# Lister toutes les gares, et possibilité de rajouter ou supprimer des gare
@bp.route('/gares', methods=['GET', 'POST'])
@login_required
def gares():
    if not current_user.admin:
        return redirect(url_for('main.index'))

    form = AddGareForm()
    if form.validate_on_submit():
        gare = Gare(nom=form.nom.data, ville=form.ville.data)
        db.session.add(gare)
        db.session.commit()
        flash('Nouvelle gare créée', 'success')
        flash(f'id: {gare.id}, {form.ville.data} - {form.nom.data}', 'info')
        return redirect(url_for('edit.gares'))
    gares = Gare.query.all()
    return render_template('edit/gares.html', title='Gares', gares=gares, form=form)


# Supprimer une gare
@bp.route('/gares/delete/<ville>/<nom>')
@login_required
def delete_gare(ville, nom):
    if not current_user.admin:
        return redirect(url_for('main.index'))

    gare = Gare.query.filter_by(ville=ville, nom=nom).first()
    if gare is None:
        flash('La gare {} à {} n\'existe pas.'.format(nom, ville), 'danger')
        return redirect(url_for('edit.gares'))
    db.session.delete(gare)
    db.session.commit()
    flash('La gare {} à {} a bien été supprimée'.format(nom, ville), 'success')
    return redirect(url_for('edit.gares'))


# CLIENTS
# =======

# Lister tous les clients et possibilité de supprimer des clients
@bp.route('/clients')
@login_required
def clients():
    if not current_user.admin:
        return redirect(url_for('main.index'))

    clients = db.session.query(Client.id, Client.pseudo, Client.nom, Client.prenom, Client.age, Client.argent,
                               Client.admin, Reduction.type).outerjoin(Reduction).filter(Client.admin==False)

    return render_template('edit/clients.html', title='Clients', clients=clients.all())


# Supprimer un client
@bp.route('/clients/delete/<id>')
@login_required
def delete_client(id):
    if not current_user.admin:
        return redirect(url_for('main.index'))

    client = Client.query.filter_by(id=id).first()
    if client is None:
        flash('Le client {} n\'existe pas.'.format(id), 'danger')
        return redirect(url_for('edit.clients'))
    elif client.admin:
        flash('Vous ne pouvez pas supprimez l\'administrateur!', 'danger')
        return redirect(url_for('edit.clients'))
    db.session.delete(client)
    db.session.commit()
    flash('Le client {} {} {} a bien été supprimée de la base de donnée'.format(id, client.nom, client.prenom),
          'success')
    return redirect(url_for('edit.clients'))


# REDUCTIONS
# ==========

# Lister toutes les réductions et possibilité de supprimer des réductions
@bp.route('/reductions', methods=['GET', 'POST'])
@login_required
def reductions():
    if not current_user.admin:
        return redirect(url_for('main.index'))

    form = AddReductionForm()
    if form.validate_on_submit():
        reduction = Reduction(type=form.type.data, pourcentage=form.pourcentage.data, prix=form.prix.data)
        db.session.add(reduction)
        db.session.commit()
        flash('Nouvelle réduction créée', 'info')
        return redirect(url_for('edit.reductions'))
    reductions = Reduction.query.all()
    return render_template('edit/reductions.html', title='Réductions', reductions=reductions, form=form)


# Supprimer une réduction
@bp.route('/reductions/delete/<id>')
@login_required
def delete_reduction(id):
    if not current_user.admin:
        return redirect(url_for('main.index'))

    reduction = Reduction.query.filter_by(id=id).first()
    if reduction is None:
        flash('La reduction {} n\'existe pas.'.format(id), 'danger')
        return redirect(url_for('edit.reductions'))
    db.session.delete(reduction)
    db.session.commit()
    flash('La reduction {} ({}) a bien été supprimée de la base de donnée'.format(id, reduction.type), 'success')
    return redirect(url_for('edit.reductions'))


# VOYAGES
# =====

# Lister tous les voyages, et possibilité de rajouter ou supprimer des voyages
@bp.route('/voyages', methods=['GET', 'POST'])
@login_required
def voyages():
    if not current_user.admin:
        return redirect(url_for('main.index'))

    # ajouter un voyage
    form = AddVoyageForm()

    form.train.choices = []

    gares = Gare.query.all()
    choix_gares = [(gare.id, '{} - {}'.format(gare.ville, gare.nom)) for gare in gares]
    form.gareDepart.choices = choix_gares
    choix_gares_arrivee = choix_gares[1:]
    form.gareArrivee.choices = choix_gares_arrivee

    if request.method == 'POST':
        form.gareArrivee.choices = choix_gares
        trains = Train.query.all()
        choix_trains = [(train.numTrain, 'Train n°{}'.format(train.numTrain)) for train in trains]
        form.train.choices = choix_trains

        if form.validate_on_submit():
            voyage = Voyage(horaireDepart=form.horaireDepart.data, horaireArrivee=form.horaireArrivee.data,
                            idGareDepart=form.gareDepart.data, idGareArrivee=form.gareArrivee.data,
                            numTrain=form.train.data, prixClasse1=form.prixClasse1.data,
                            prixClasse2=form.prixClasse2.data)
            db.session.add(voyage)
            train = Train.query.filter_by(numTrain=form.train.data).first()
            for voiture in train.voitures:
                for place in voiture.places:
                    billet = Billet(voyage=voyage, place=place)
                    db.session.add(billet)
            db.session.commit()
            flash('Nouveau voyage créé', 'info')
            current_app.logger.info('redirect')
            return redirect(url_for('edit.voyages'))
        else:
            current_app.logger.error('Erreur de formulaire')

    else:
        form.prixClasse1.data = randint(50, 100)
        form.prixClasse2.data = randint(20, form.prixClasse1.data)

    # lister les voyages
    voyages = Voyage.query.all()
    current_app.logger.info('render_template')
    return render_template('edit/voyages.html', title='Voyages', voyages=voyages, form=form,
                           startDate=datetime.utcnow().strftime('%d/%m/%Y %H:%M'))


# Visualiser un voyage en particulier, avec les billets
@bp.route('/voyages/<id>')
@login_required
def edit_voyage(id):
    if not current_user.admin:
        return redirect(url_for('main.index'))

    voyage = Voyage.query.filter_by(id=id).first_or_404()
    gareDepart = Gare.query.filter_by(id=voyage.idGareDepart).first()
    gareArrivee = Gare.query.filter_by(id=voyage.idGareArrivee).first()
    billets = voyage.billets.all()
    return render_template('edit/voyage.html', title='Edit Voyage', billets=billets, gareDepart=gareDepart,
                           gareArrivee=gareArrivee, jumbotron_title=f'Voyage n°{voyage.id}', voyage=voyage)


# Supprimer un voyage
@bp.route('/voyages/delete/<id>')
@login_required
def delete_voyage(id):
    if not current_user.admin:
        return redirect(url_for('main.index'))

    voyage = Voyage.query.filter_by(id=id).first()
    if voyage is None:
        flash('Le voyage {} n\'existe pas.'.format(id), 'danger')
        return redirect(url_for('edit.voyages'))
    db.session.delete(voyage)
    db.session.commit()
    flash('La voyage {} a bien été supprimé'.format(id), 'success')
    return redirect(url_for('edit.voyages'))


# Renvoie tous les trains qui sot disponibles aux horaires indiquées
@bp.route('/trains/<horaireDepart>/<horaireArrivee>')
@login_required
def get_trains_horaires(horaireDepart, horaireArrivee):
    if not current_user.admin:
        return redirect(url_for('main.index'))

    horaireDepart = datetime.strptime(horaireDepart, '%d-%m-%YT%H:%M')
    horaireArrivee = datetime.strptime(horaireArrivee, '%d-%m-%YT%H:%M')

    trains_occupes = db.session.query(Train.numTrain, Voyage.horaireDepart).outerjoin(Voyage) \
        .filter(or_(and_(Voyage.horaireDepart < horaireDepart, horaireDepart < Voyage.horaireArrivee),
                    and_(Voyage.horaireDepart < horaireArrivee, horaireArrivee < Voyage.horaireArrivee),
                    and_(Voyage.horaireDepart < horaireDepart, horaireArrivee < Voyage.horaireArrivee),
                    and_(horaireDepart < Voyage.horaireDepart, Voyage.horaireArrivee < horaireArrivee))
                ).cte(name="trains_occupes")

    trains_libres = db.session.query(Train).outerjoin(trains_occupes,
                                                      Train.numTrain == trains_occupes.c.numTrain).filter(
        trains_occupes.c.horaireDepart == None
    )

    current_app.logger.info(trains_libres)
    current_app.logger.info(trains_libres.all())

    data = [(train.numTrain, 'Train n°{}'.format(train.numTrain)) for train in trains_libres]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response
