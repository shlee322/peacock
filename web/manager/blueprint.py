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

    return render_template('manager/dashboard/dashboard.html', **locals())


@blueprint.route('/manager/<service_id>/eventviewer')
def manager_service_eventviewer(service_id):
    from .funcs import get_service_name, get_menus

    service_name = get_service_name(service_id)
    menus = get_menus('eventviewer')

    return render_template('manager/eventviewer/eventviwer.html', **locals())


@blueprint.route('/manager/<service_id>/eventviewer/_ajax/get_event_list')
def manager_service_eventviwer_get_event_list(service_id):
    import json
    from couchbase.bucket import Bucket as CouchbaseBucket
    from couchbase.views.iterator import View, Query

    log_db = CouchbaseBucket('couchbase://localhost/events')

    timestamp = int(request.args['timestamp'])

    q = Query(
        descending=True,
        mapkey_range=[
            [service_id, timestamp],
            [service_id, int(request.args.get('start_timestamp', 0))]
        ],
        limit=20
    )

    view = View(log_db, "events", "eventviewer", query=q)

    result_data = []
    for result in view:
        result_obj = {
            'timestamp': result.value['timestamp'],
            'entity': result.value['entity'],
            'event_name': result.value.get('event_name')
        }

        if result.value.get('timestamp_length'):
            result_obj['timestamp_length'] = result.value.get('timestamp_length')
        else:
            result_obj['timestamp_length'] = 0

        if result.value.get('data'):
            result_obj['data'] = json.dumps(result.value.get('data'))[:100]

        result_data.insert(0, result_obj)

    return jsonify({
        'status': 'succeeded',
        'data': result_data
    })



@blueprint.route('/manager/<service_id>/eventviewer/_ajax/get_entity_timeline')
def manager_service_eventviwer_get_entity_timeline(service_id):
    entity_kind = request.args['kind']
    entity_id = request.args['id']

    start_timestamp = int(request.args['start_timestamp'])
    end_timestamp = int(request.args['end_timestamp'])

    from couchbase.bucket import Bucket as CouchbaseBucket
    from couchbase.views.iterator import View, Query

    log_db = CouchbaseBucket('couchbase://localhost/events')

    q = Query(
        mapkey_range=[
            [service_id, entity_kind, entity_id, start_timestamp, ],
            [service_id, entity_kind, entity_id, end_timestamp, Query.STRING_RANGE_END]
        ],
        limit=200
    )

    view = View(log_db, "events", "entity_timeline", query=q)

    result_data = []
    for result in view:
        result_obj = {
            'id': result.docid,
            'type': result.value['type'],
            'timestamp': result.value['timestamp']
        }
        if result.value.get('timestamp_length'):
            result_obj['timestamp_length'] = result.value.get('timestamp_length')
        elif result_obj['type'] == 'event':
            result_obj['timestamp_length'] = 0

        if result.value.get('target'):
            result_obj['target'] = result.value.get('target')

        if result.value.get('event_name'):
            result_obj['event_name'] = result.value.get('event_name')

        result_data.append(result_obj)

    return jsonify({
        'status': 'succeeded',
        'data': result_data
    })


@blueprint.route('/manager/<service_id>/analyzer')
def manager_service_analyzer(service_id):
    from .funcs import get_service_name, get_menus

    service_name = get_service_name(service_id)
    menus = get_menus('analyzer')

    return render_template('manager/analyzer/analyzer.html', **locals())


@blueprint.route('/manager/<service_id>/analyzer/_ajax/add_analyzer', methods=['POST'])
def manager_analyzer_ajax_add_analyzer(service_id):
    data = request.get_json()

    if data['group']['entity_kind'] == '':
        data['group']['entity_kind'] = None

    print(data)
    return jsonify({
        'status': 'failed',
        'message': 'test'
    })


@blueprint.route('/manager/<service_id>/setting')
def manager_service_setting(service_id):
    from .funcs import get_service_name, get_menus

    service_name = get_service_name(service_id)
    menus = get_menus('setting')

    from .funcs import get_service_uid
    service_uid = get_service_uid(service_id)

    cur = g.db.cursor()
    cur.execute('SELECT `id`, `key` FROM `service_server_keys` WHERE `service_uid`=%(service_uid)s;', {
        'service_uid': service_uid
    })

    server_keys = []
    rows = cur.fetchall()
    for row in rows:
        server_keys.append({
            'id': row[0],
            'key': row[1]
        })

    return render_template('manager/setting/serverkey.html', **locals())


@blueprint.route('/manager/<service_id>/setting/_ajax/add_server', methods=['POST'])
def manager_service_setting_ajax_add_server(service_id):
    data = request.get_json()

    key_id = data['id']
    key = data['key']

    try:
        from Crypto.PublicKey import RSA

        key = RSA.importKey(key).exportKey()
    except ValueError:
        return jsonify({
            'status': 'failed',
            'message': '지원하지 않는 키 형식이거나 키가 올바르지 않습니다.'
        })

    from .funcs import get_service_uid
    service_uid = get_service_uid(service_id)
    from flask import g
    # 아이디 체크
    cur = g.db.cursor()
    cur.execute('SELECT * FROM `service_server_keys` WHERE `service_uid`=%(service_uid)s AND `id`=%(id)s;', {
        'service_uid': service_uid,
        'id': key_id
    })

    if cur.fetchone():
        return jsonify({
            'status': 'failed',
            'message': '이미 존재하는 ID입니다'
        })

    import pymysql

    try:
        cur.execute('INSERT INTO `service_server_keys` (`service_uid`, `id`, `key`) ' +
                    'VALUES (%(service_uid)s, %(id)s, %(key)s)', {
            'service_uid': service_uid,
            'id': key_id,
            'key': key
        })
    except pymysql.MySQLError:
        g.db.rollback()

        return jsonify({
            'status': 'failed',
            'message': '알 수 없는 에러가 발생하였습니다. 잠시후 다시 시도해주세요.'
        })

    g.db.commit()

    return jsonify({
        'status': 'succeeded'
    })