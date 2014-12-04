from flask import Blueprint, render_template

blueprint = Blueprint('manager', __name__, template_folder='templates')


@blueprint.route('/manager/')
def manager_root():
    return render_template('manager/setting/serverkey.html')