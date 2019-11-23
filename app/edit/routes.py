from flask import render_template, flash, redirect, url_for
from app import db
from app.edit import bp
from app.models import Train, Voiture, Gare, Client, Voyage
from app.edit.forms import AddTrainForm, AddVoitureForm, AddGareForm, AddVoyageForm


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
            voiture = Voiture(nbPlaces=form.nbPlacesParVoiture.data, numVoiture=i + 1, train=train)
            db.session.add(voiture)
        db.session.commit()
        flash('Nouveau train créé', 'info')
    trains = Train.query.all()
    return render_template('edit/trains.html', title='Trains', trains=trains, form=form)


# Visualiser un train en particulier
@bp.route('/trains/<numTrain>', methods=['GET', 'POST'])
def edit_train(numTrain):
    train = Train.query.filter_by(numTrain=numTrain).first_or_404()
    voitures = train.voitures.order_by(Voiture.numVoiture)
    numTotVoitures = voitures.count()
    form = AddVoitureForm()
    if form.validate_on_submit():
        numVoiture = 1
        while numVoiture <= numTotVoitures and numVoiture == voitures[numVoiture - 1].numVoiture:
            numVoiture += 1
        voiture = Voiture(nbPlaces=form.capacite.data, numVoiture=numVoiture, train=train)
        db.session.add(voiture)
        db.session.commit()
        flash('Voiture ajoutée', 'info')
    voitures = train.voitures.order_by(Voiture.numVoiture)
    return render_template('edit/train.html', title='Edit Train', jumbotron_title='Train n°{}'.format(train.numTrain),
                           train=train, voitures=voitures, form=form)


# Supprimer un train
@bp.route(('/trains/delete/<numTrain>'))
def delete_train(numTrain):
    train = Train.query.filter_by(numTrain=numTrain).first()
    if train is None:
        flash('Train number {} not found.'.format(numTrain), 'danger')
        return redirect(url_for('edit.trains'))
    db.session.delete(train)
    db.session.commit()
    flash('Train number {} has been deleted.'.format(numTrain), 'success')
    return redirect(url_for('edit.trains'))


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


# VOYAGES
# =====

# Lister tous les voyages, et possibilité de rajouter ou supprimer des voyages
@bp.route('/voyages', methods=['GET', 'POST'])
def voyages():
    form = AddVoyageForm()
    gares = Gare.query.all()
    choix_gares = [(gare.id, '{} - {}'.format(gare.ville, gare.nom)) for gare in gares]
    form.gareDepart.choices = choix_gares
    form.gareArrivee.choices = choix_gares
    trains = Train.query.all()
    choix_trains = [(train.numTrain, train.numTrain) for train in trains]
    form.train.choices = choix_trains
    if form.validate_on_submit():
        voyage = Voyage(horaireDepart=form.horaireDepart.data, horaireArrivee=form.horaireArrivee.data,
                        idGareDepart=form.gareDepart.data, idGareArrivee=form.gareArrivee.data,
                        numTrain=form.train.data)
        db.session.add(voyage)
        db.session.commit()
        flash('Nouveau voyage créé', 'info')
    voyages = Voyage.query.join(Gare, Voyage.idGareDepart==Gare.id).all()
    return render_template('edit/voyages.html', title='Voyages', voyages=voyages, form=form)


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
