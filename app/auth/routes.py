from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import Client


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Client.query.filter_by(pseudo=form.pseudo.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Votre pseudo ou mot de passe est incorrect', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Connexion', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            user = Client(pseudo=form.pseudo.data, nom=form.nom.data, prenom=form.prenom.data, age=form.age.data,
                          argent=300)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Félicitations, vous avez créer votre compte !', 'info')
            current_app.logger.info('redirect')
            return redirect(url_for('auth.login'))
        else:
            current_app.logger.error('Erreur de formulaire')

    current_app.logger.info('render_template')
    return render_template('auth/register.html', title='Créer son compte', form=form)
