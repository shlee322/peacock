from flask import Blueprint, render_template

blueprint = Blueprint('auth', __name__, template_folder='templates')

@blueprint.route('/auth')
def main_auth():
    pass
