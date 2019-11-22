from flask import render_template, flash
from app import db
from app.edit import bp
from app.models import Train
from app.edit.forms import AddTrainForm


# Lister tous les trains, et possibilité de rajouter ou supprimer des trains
@bp.route('/trains', methods=['GET', 'POST'])
def trains():
    form = AddTrainForm()
    if form.validate_on_submit():
        train = Train()
        db.session.add(train)
        db.session.commit()
        flash('Nouveau train créé', 'info')
    trains = Train.query.all()
    return render_template('edit/trains.html', title='Trains', trains=trains, form=form)
