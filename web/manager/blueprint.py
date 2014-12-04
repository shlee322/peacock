from flask import Blueprint, request, render_template, jsonify, g

blueprint = Blueprint('manager', __name__, template_folder='templates')


@blueprint.before_request
def manager_before_request():
    from flask import session
    if not session.get('account_uid'):
        from flask import redirect
        return redirect('/')

    from .funcs import get_account_services
    g.services = get_account_services()


@blueprint.route('/manager/')
def manager_root():
    from .funcs import get_account_services
    services = get_account_services()

    from flask import redirect
    if len(services) < 1:
        return redirect('/manager/create')
    else:
        return redirect('/manager/%s/' % services[0]['id'])


@blueprint.route('/manager/create')
def manager_create():
    return render_template('manager/create/create.html')


@blueprint.route('/manager/create/_ajax/create', methods=['POST'])
def manager_create_ajax():
    data = request.get_json()

    service_id = data['service_id']
    service_name = data['service_name']

    import re
    if not re.match("^[a-z0-9-]{8,128}$", service_id):
        return jsonify({
            'status': 'failed',
            'message': 'Service ID는 a-z, 0-9, -로만 이루어질 수 있으며 8자부터 128자 사이여야 합니다'
        })

    if len(service_name) > 64:
        return jsonify({
            'status': 'failed',
            'message': 'Service Name는 64자 이하만 사용할 수 있습니다'
        })

    from flask import g
    cur = g.db.cursor()
    cur.execute('SELECT * FROM `services` WHERE `service_id`=%(service_id)s;', {
        'service_id': service_id
    })

    if cur.fetchone():
        return jsonify({
            'status': 'failed',
            'message': '이미 존재하는 Service ID입니다'
        })

    from flask import session
    import pymysql
    try:
        cur.execute('INSERT INTO `services` (`service_id`, `service_name`, `create_time`) ' +
                    'VALUES (%(service_id)s, %(service_name)s, now());', {
            'service_id': service_id,
            'service_name': service_name
        })

        service_uid = g.db.insert_id()

        cur.execute("INSERT INTO `service_members` (`service_uid`, `account_uid`, `permission`) " +
                    "VALUES (%(service_uid)s, %(account_uid)s, 'admin');", {
            'service_uid': service_uid,
            'account_uid': session['account_uid']
        })

        g.db.commit()
    except pymysql.MySQLError:
        g.db.rollback()
        return jsonify({
            'status': 'failed',
            'message': '알 수 없는 에러가 발생하였습니다. 잠시후 다시 시도해주세요.'
        })

    return jsonify({
        'status': 'succeeded',
        'data': {
            'service_id': service_id
        }
    })


@blueprint.route('/manager/<service_id>/')
def manager_service_main(service_id):
    from .funcs import get_service_name
    service_name = get_service_name(service_id)
    from flask import redirect
    return redirect('/manager/%s/dashboard' % service_id)


@blueprint.route('/manager/<service_id>/dashboard')
def manager_service_dashboard(service_id):
    from .funcs import get_service_name, get_menus
    service_name = get_service_name(service_id)
    menus = get_menus('dashboard')

    return render_template('manager/setting/serverkey.html', **locals())


@blueprint.route('/manager/<service_id>/eventviewer')
def manager_service_eventviewer(service_id):
    from .funcs import get_service_name, get_menus
    service_name = get_service_name(service_id)
    menus = get_menus('eventviewer')

    return render_template('manager/setting/serverkey.html', **locals())


@blueprint.route('/manager/<service_id>/analyzer')
def manager_service_analyzer(service_id):
    from .funcs import get_service_name, get_menus
    service_name = get_service_name(service_id)
    menus = get_menus('analyzer')

    return render_template('manager/setting/serverkey.html', **locals())


@blueprint.route('/manager/<service_id>/setting')
def manager_service_setting(service_id):
    from .funcs import get_service_name, get_menus
    service_name = get_service_name(service_id)
    menus = get_menus('setting')

    return render_template('manager/setting/serverkey.html', **locals())
