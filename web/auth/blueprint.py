from flask import Blueprint, request, g, jsonify

blueprint = Blueprint('auth', __name__, template_folder='templates')


@blueprint.route('/auth', methods=['POST'])
def main_auth():
    data = request.get_json()

    service_id = data.get('service_id')
    server_key_id = data.get('server_key_id')

    from manager.funcs import get_service_uid
    service_uid = get_service_uid(service_id)

    if not service_uid:
        return jsonify({
            'status': 'failed',
            'message': '해당 서비스가 존재하지 않습니다'
        })

    cur = g.db.cursor()
    cur.execute('SELECT `uid`, `key` FROM `service_server_keys` WHERE `service_uid`=%(service_uid)s and `id`=%(server_key_id)s'
                , {'service_uid': service_uid, 'server_key_id': server_key_id})

    server_data = cur.fetchone()
    if not server_data:
        return jsonify({
            'status': 'failed',
            'message': '해당 서버 키가 존재하지 않습니다'
        })

    public_key = server_data[1]

    import binascii
    key = binascii.unhexlify(data.get('key'))
    sign = binascii.unhexlify(data.get('sign'))

    from Crypto.PublicKey import RSA

    public_key = RSA.importKey(public_key)

    import hashlib
    print(public_key.verify(hashlib.sha256(key).digest(), sign))

    return jsonify({
        'status': 'succeeded',
        'data': {
            'token': 'kr-elab-test',
            'logger': {
                'zmq': [
                    '127.0.0.1:6000'
                ]
            }
        }
    })
