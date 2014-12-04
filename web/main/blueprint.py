from flask import Blueprint, render_template, request, jsonify

blueprint = Blueprint('main', __name__, template_folder='templates')


@blueprint.route('/')
def main_root():
    return render_template('main/main.html')


@blueprint.route('/_ajax/login', methods=['POST'])
def main_login():
    data = request.get_json()

    return jsonify({
        'status': 'failed',
        'message': '존재하지 않는 아이디입니다'
    })
