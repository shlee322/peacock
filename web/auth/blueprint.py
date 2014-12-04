from flask import Blueprint, render_template

blueprint = Blueprint('auth', __name__, template_folder='templates')


@blueprint.route('/auth', methods=['POST'])
def main_auth():
    from flask import jsonify
    return jsonify({
        'status': 'succeeded',
        'token': 'kr-elab-test',
        'logger': {
            'zmq': [
                '127.0.0.1:6000'
            ]
        }
    })
