def get_account_services():
    from flask import g, session

    cur = g.db.cursor()
    cur.execute(
        'SELECT `service_id`, `service_name` FROM `service_members` INNER JOIN services ON service_members.service_uid = services.uid WHERE `account_uid`=%(account_uid)s;',
        {
            'account_uid': session['account_uid']
        })

    services = []
    rows = cur.fetchall()
    for row in rows:
        services.append({
            'id': row[0],
            'name': row[1]
        })

    return services


def get_service_name(service_id):
    from flask import g

    for service in g.services:
        if service['id'] == service_id:
            return service['name']
    return None


def get_menus(menu_id):
    return [
        {'id': 'dashboard', 'name': 'Dashboard', 'active': menu_id == 'dashboard'},
        {'id': 'eventviewer', 'name': 'Event Viewer', 'active': menu_id == 'eventviewer'},
        {'id': 'analyzer', 'name': 'Analyzer', 'active': menu_id == 'analyzer'},
        {'id': 'setting', 'name': 'Setting', 'active': menu_id == 'setting'},
    ]
