from flask import render_template, send_from_directory
from app.main import bp
from flask_login import current_user, login_required
from app.main.forms import RechercheTrajet
from app.models import Voyage, Gare


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
