from couchbase.views.iterator import View, Query
from jobserver import database


def process_analyzer_group(message):
    analyzer = database.analyzer_db.get(message['analyzer_id']).value

    q = Query(
        inclusive_end=True,
        mapkey_range=[
            [analyzer['service']['id'], message['analyzer_id'], message['group'][0], message['group'][1], ],
            [analyzer['service']['id'], message['analyzer_id'], message['group'][0], message['group'][1], Query.STRING_RANGE_END]
        ],
        limit=1000000
    )

    view = View(database.analyzer_input_db, "input", "group", query=q)
    input_data = []
    for result in view:
        input_data.append(database.event_db.get(result.value).value)

    group_result = group_reduce(input_data, analyzer['processor_script'])
    result_key = "%s_%s_%s_%s" % (analyzer['service']['id'], message['analyzer_id'],
                                  message['group'][0], message['group'][1])

    database.analyzer_result_db.upsert(result_key, {
        'service': analyzer['service'],
        'analyzer_id': message['analyzer_id'],
        'group': message['group'],
        'data': group_result
    })

    # TODO : 이제 다시 인풋으로


def _count(input_data):
    return len(input_data)


def group_reduce(input_data, script):
    import lupa
    from lupa import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=False)
    g = lua.globals()
    g.input = input_data
    g._count = _count
    output = lua.eval(script)
    return output
