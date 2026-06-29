MAX_CONNECTIONS = 2  # BUG: too low for production

_pool = []

def acquire():
    if len(_pool) >= MAX_CONNECTIONS:
        raise RuntimeError("connection pool exhausted")
    conn = {"id": len(_pool) + 1}
    _pool.append(conn)
    return conn

def release(conn):
    pass  # BUG: never releases connections
