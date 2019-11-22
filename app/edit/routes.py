from flask import render_template, flash, redirect, url_for
from app import db
from app.edit import bp
from app.models import Train, Voiture
from app.edit.forms import AddTrainForm, AddVoitureForm


# Lister tous les trains, et possibilité de rajouter ou supprimer des trains
@bp.route('/trains', methods=['GET', 'POST'])
def trains():
    form = AddTrainForm()
    if form.validate_on_submit():
        train = Train()
        db.session.add(train)
        for i in range(form.nbVoitures.data):
            voiture = Voiture(nbPlaces=form.nbPlacesParVoiture.data, numVoiture=i+1, train=train)
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
        while numVoiture <= numTotVoitures and numVoiture == voitures[numVoiture-1].numVoiture:
            numVoiture += 1
        voiture = Voiture(nbPlaces=form.capacite.data, numVoiture=numVoiture, train=train)
        db.session.add(voiture)
        db.session.commit()
        flash('Voiture ajoutée', 'info')
    voitures = train.voitures.order_by(Voiture.numVoiture)
    return render_template('edit/train.html', title='Edit Train', train=train, voitures=voitures, form=form)


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
