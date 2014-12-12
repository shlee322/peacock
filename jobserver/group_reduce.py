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
