def get_account_services():
    from flask import g, session
    cur = g.db.cursor()
    cur.execute('SELECT `service_id`, `service_name` FROM `service_members` INNER JOIN services ON service_members.service_uid = services.uid WHERE `account_uid`=%(account_uid)s;', {
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
