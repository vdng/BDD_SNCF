from flask import render_template, send_from_directory, redirect, url_for, flash
from app.main import bp
from flask_login import current_user, login_required
from app.main.forms import *
from app.models import Voyage, Gare, Reduction


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = RechercheTrajet()
    gares = Gare.query.all()
    choix_gares = [(gare.id, '{} - {}'.format(gare.ville, gare.nom)) for gare in gares]
    form.gareDepart.choices = choix_gares
    form.gareArrivee.choices = choix_gares
    if form.validate_on_submit():
        voyages = Voyage.query.filter_by(idGareDepart=form.gareDepart.data, idGareArrivee=form.gareArrivee.data)
        return render_template('index.html', title='Accueil', voyages=voyages, form=form)
    return render_template('index.html', title='Accueil', form=form)


# Visualiser un voyage en particulier, avec les billets
@bp.route('/voyages/<id>')
def voyage(id):
    voyage = Voyage.query.filter_by(id=id).first_or_404()
    billets = voyage.billets.all()
    return render_template('voyage.html', title='Voyage', billets=billets,
                           jumbotron_title='{} {} -> {} {}'.format(voyage.gareDepart.ville, voyage.gareDepart.nom,
                                                                   voyage.gareArrivee.ville, voyage.gareArrivee.nom))


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(bp.root_path, 'favicon.ico')


@bp.route('/moncompte', methods=['GET', 'POST'])
@login_required
def moncompte():
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

    voyages = Voyage.query.all()
    return render_template('moncompte.html', title='Mon compte', voyages=voyages, form_reduction=form_reduction,
                           form_portefeuille=form_portefeuille, reduction=reduction,
                           jumbotron_title='{}'.format(current_user.pseudo))
