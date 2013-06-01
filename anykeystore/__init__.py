try:
    import sqlite3
except ImportError:
    pass
else:
    from sqlite_backend import Sqlite

try:
    import pymongo
except ImportError:
    pass
else:
    from mongodb_backend import MongoDB

try:
    import riak
except ImportError:
    pass
else:
    from riak_backend import Riak
