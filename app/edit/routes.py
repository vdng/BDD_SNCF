from flask import render_template, flash, redirect, url_for, request
from app import db
from app.edit import bp
from app.models import *
from app.edit.forms import *


@bp.route('/')
def edit_index():
    return render_template('edit/edit_index.html', title='Edit')


# TRAINS
# ======

# Lister tous les trains, et possibilité de rajouter ou supprimer des trains
@bp.route('/trains', methods=['GET', 'POST'])
def trains():
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
        flash('Nouveau train créé', 'info')
        return redirect(url_for('edit.trains'))
    trains = Train.query.all()
    return render_template('edit/trains.html', title='Trains', trains=trains, form=form)


# Visualiser un train en particulier, possibilité de rajouter et supprimer des voitures
@bp.route('/trains/<numTrain>', methods=['GET', 'POST'])
def edit_train(numTrain):
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
        flash('Voiture ajoutée', 'info')
        return redirect(url_for('edit.edit_train', numTrain=numTrain))

    voitures = train.voitures.order_by(Voiture.numVoiture)
    return render_template('edit/train.html', title='Edit Train', jumbotron_title='Train n°{}'.format(train.numTrain),
                           train=train, voitures=voitures, form=form)


# Supprimer un train
@bp.route('/trains/delete/<numTrain>')
def delete_train(numTrain):
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
def delete_voiture(numTrain, idVoiture):
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
def gares():
    form = AddGareForm()
    if form.validate_on_submit():
        gare = Gare(nom=form.nom.data, ville=form.ville.data)
        db.session.add(gare)
        db.session.commit()
        flash('Nouvelle gare créée', 'info')
        return redirect(url_for('edit.gares'))
    gares = Gare.query.all()
    return render_template('edit/gares.html', title='Gares', gares=gares, form=form)


# Supprimer une gare
@bp.route('/gares/delete/<ville>/<nom>')
def delete_gare(ville, nom):
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
def clients():
    clients = Client.query.all()
    return render_template('edit/clients.html', title='Clients', clients=clients)


# Supprimer un client
@bp.route('/clients/delete/<id>')
def delete_client(id):
    client = Client.query.filter_by(id=id).first()
    if client is None:
        flash('Le client {} n\'existe pas.'.format(id), 'danger')
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
def reductions():
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
def delete_reduction(id):
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
def voyages():
    # ajouter un voyage
    form = AddVoyageForm()

    trains = Train.query.all()
    choix_trains = [(train.numTrain, 'Train n°{}'.format(train.numTrain)) for train in trains]
    form.train.choices = choix_trains

    gares = Gare.query.all()
    choix_gares = [(gare.id, '{} - {}'.format(gare.ville, gare.nom)) for gare in gares]
    form.gareDepart.choices = choix_gares
    choix_gares_arrivee = choix_gares[1:]
    form.gareArrivee.choices = choix_gares_arrivee

    if request.method == 'POST':
        form.gareArrivee.choices = choix_gares
        if form.validate_on_submit():
            voyage = Voyage(horaireDepart=form.horaireDepart.data, horaireArrivee=form.horaireArrivee.data,
                            idGareDepart=form.gareDepart.data, idGareArrivee=form.gareArrivee.data,
                            numTrain=form.train.data, prixClasse1=form.prixClasse1.data, prixClasse2=form.prixClasse2.data)
            db.session.add(voyage)
            train = Train.query.filter_by(numTrain=form.train.data).first()
            for voiture in train.voitures:
                for place in voiture.places:
                    billet = Billet(voyage=voyage, place=place)
                    db.session.add(billet)
            db.session.commit()
            flash('Nouveau voyage créé', 'info')
            return redirect(url_for('edit.voyages'))

    # lister les voyages
    voyages = Voyage.query.all()
    return render_template('edit/voyages.html', title='Voyages', voyages=voyages, form=form)


# Visualiser un voyage en particulier, avec les billets
@bp.route('/voyages/<id>')
def edit_voyage(id):
    voyage = Voyage.query.filter_by(id=id).first_or_404()
    billets = voyage.billets.all()
    return render_template('edit/voyage.html', title='Edit Voyage', billets=billets,
                           jumbotron_title='{} {} -> {} {}'.format(voyage.gareDepart.ville, voyage.gareDepart.nom,
                                                                   voyage.gareArrivee.ville, voyage.gareArrivee.nom))


# Supprimer un voyage
@bp.route('/voyages/delete/<id>')
def delete_voyage(id):
    voyage = Voyage.query.filter_by(id=id).first()
    if voyage is None:
        flash('Le voyage {} n\'existe pas.'.format(id), 'danger')
        return redirect(url_for('edit.voyages'))
    db.session.delete(voyage)
    db.session.commit()
    flash('La voyage {} a bien été supprimé'.format(id), 'success')
    return redirect(url_for('edit.voyages'))


# DELETE ALL
# ==========

@bp.route('/delete_all')
def delete_all():
    clients = Client.query.all()
    for client in clients:
        db.session.delete(client)
    trains = Train.query.all()
    for train in trains:
        db.session.delete(train)
    voitures = Voiture.query.all()
    for voiture in voitures:
        db.session.delete(voiture)
    places = Place.query.all()
    for place in places:
        db.session.delete(place)
    gares = Gare.query.all()
    for gare in gares:
        db.session.delete(gare)
    voyages = Voyage.query.all()
    for voyage in voyages:
        db.session.delete(voyage)
    billets = Billet.query.all()
    for billet in billets:
        db.session.delete(billet)
    db.session.commit()
    flash('Toutes les données ont été supprimées'.format(id), 'success')
    return redirect(url_for('edit.edit_index'))
