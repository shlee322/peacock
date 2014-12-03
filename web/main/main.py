from flask import Blueprint, render_template

blueprint = Blueprint('main', __name__, template_folder='templates')


@blueprint.route('/')
def main_root():
    return render_template('main/main.html')
