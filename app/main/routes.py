from flask import render_template, send_from_directory
from app.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Accueil')


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(bp.root_path, 'favicon.ico')
