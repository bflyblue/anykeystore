import sqlite3
import json
from util import check_bucket_name

class SqliteBucket:
    def __init__(self, conn, name, indexfn=None):
        self.conn = conn
        self.name = name
        self.indexfn = indexfn

    def get(self, key, default=None):
        key = str(key)
        # lookup key/value pair
        c = self.conn.cursor()
        c.execute('select value from "%s" where key=?' % self.name, (key,))
        row = c.fetchone()
        if row:
            return json.loads(row[0])
        return default

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        key = str(key)
        # upsert key/value pair
        self.conn.execute('insert or replace into "%s" (key, value) values (?, ?)' % self.name, (key, json.dumps(value)))
        # clear out stale 2i entries pointing to this key
        self.conn.execute('delete from "%s_i" where key=?' % self.name, (key,))
        # create new 2i entries pointing to this key
        if self.indexfn:
            for index, val in self.indexfn(key, value):
                self.conn.execute('insert or replace into "%s_i" (ikey, ivalue, key) values (?, ?, ?)' % self.name, (str(index), str(val), key))
        self.conn.commit()

    def __delitem__(self, key):
        key = str(key)
        # delete key/value pair, 2i entries dropped via cascade
        self.conn.execute('delete from "%s" where key=?' % self.name, (key,))
        self.conn.commit()

    def keys(self):
        c = self.conn.cursor()
        c.execute('select key from "%s"' % self.name)
        for key, in c.fetchall():
            yield key

    def items(self):
        c = self.conn.cursor()
        c.execute('select key, value from "%s"' % self.name)
        for key, val in c.fetchall():
            yield key, json.loads(val)

    def find(self, spec):
        results = []
        for i, (index, val) in enumerate(spec.items()):
            c = self.conn.cursor()
            c.execute('select key from "%s_i" where ikey=? and ivalue=?' % self.name, (str(index), str(val)))
            keys = set([r[0] for r in c.fetchall()])
            if i == 0:
                results = keys
            else:
                results.intersection_update(keys)
            if not results:
                break

        for key in results:
            yield key, self[key]

class Sqlite:
    def __init__(self, filename='keystore.db'):
        self.conn = sqlite3.connect(filename)

    def bucket(self, name, indexfn=None):
        check_bucket_name(name)

        # Create table for bucket, and table for indices
        self.conn.execute('pragma foreign_keys=on')
        self.conn.execute('create table if not exists "%(name)s" '
                          '(key text primary key, value text)'
                          % {'name': name})
        self.conn.execute('create table if not exists "%(name)s_i" '
                          '(ikey text, ivalue text, key text references "%(name)s" (key) on delete cascade on update cascade)'
                          % {'name': name})
        self.conn.execute('create index if not exists "%(name)s_i_kv" on "%(name)s_i" (ikey, ivalue)'
                          % {'name': name})
        self.conn.execute('create index if not exists "%(name)s_i_key" on "%(name)s_i" (key)'
                          % {'name': name})
        self.conn.commit()

        return SqliteBucket(self.conn, name, indexfn)
