from flask import Blueprint, render_template, request, jsonify

blueprint = Blueprint('main', __name__, template_folder='templates')


@blueprint.route('/')
def main_root():
    return render_template('main/main.html')


@blueprint.route('/_ajax/login', methods=['POST'])
def main_login():
    data = request.get_json()

    from flask import g
    # 아이디 체크
    username = data['username']
    cur = g.db.cursor()
    cur.execute('SELECT `uid`, `password` FROM `accounts` WHERE `username`=%(username)s;', {
        'username': username
    })

    account_obj = cur.fetchone()
    if not account_obj:
        return jsonify({
            'status': 'failed',
            'message': '존재하지 않는 아이디입니다'
        })

    password = data['password'][:64].encode('utf-8')
    password_hash = account_obj[1].encode('utf-8')
    import bcrypt
    if bcrypt.hashpw(password, password_hash) != password_hash:
        return jsonify({
            'status': 'failed',
            'message': '비밀번호가 올바르지 않습니다'
        })

    from flask import session
    session['account_uid'] = account_obj[0]
    session['account_username'] = username

    return jsonify({
        'status': 'succeeded'
    })


@blueprint.route('/_ajax/join', methods=['POST'])
def main_join():
    import re
    data = request.get_json()

    # 아이디 검증
    username = data['username']
    if not re.match("^[a-z0-9_.-]{4,64}$", username):
        return jsonify({
            'status': 'failed',
            'message': '아이디는 a-z, 0-9, _, ., -로만 이루어질 수 있으며 4자부터 64자 사이여야 합니다'
        })

    # 비밀번호 해시
    password = data['password']
    import bcrypt
    password_hash = bcrypt.hashpw(password[:64].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # 이메일 검증
    email = data['email']
    if not re.match("^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$", email):
        return jsonify({
            'status': 'failed',
            'message': '이메일 형식이 옳바르지 않습니다'
        })

    from flask import g
    # 아이디 체크
    cur = g.db.cursor()
    cur.execute('SELECT * FROM `accounts` WHERE `username`=%(username)s;', {
        'username': username
    })

    if cur.fetchone():
        return jsonify({
            'status': 'failed',
            'message': '이미 존재하는 아이디입니다'
        })

    import pymysql
    try:
        cur.execute('INSERT INTO `accounts` (`username`, `password`, `email`, `create_time`) ' +
                    'VALUES (%(username)s, %(password)s, %(email)s, now());', {
            'username': username,
            'password': password_hash,
            'email': email
        })
    except pymysql.MySQLError:
        g.db.rollback()
        return jsonify({
            'status': 'failed',
            'message': '알 수 없는 에러가 발생하였습니다. 잠시후 다시 시도해주세요.'
        })

    account_uid = g.db.insert_id()

    g.db.commit()

    from flask import session
    session['account_uid'] = account_uid
    session['account_username'] = username

    return jsonify({
        'status': 'succeeded'
    })
