===========
anykeystore
===========

Anykeystore is a wrapper around several backends to make them appear as basic
key-value stores. Typical usage often looks like this::

    #!/usr/bin/env python

    import anykeystore

    ks = anykeystore.Sqlite()
    b  = ks.bucket('test')

    b['key1'] = 'value1'
    b['key2'] = {'name': 'bob'}

    assert b['key1'] == 'value1'

An index function may be specified for buckets, which can be used to tag
key-value pairs as they are stored in the bucket. The ``find()`` method is
used to lookup key-value pairs based on their tags::

    def indexfn(key, val):
        yield ('name', val['name'])

    b2 = k2.bucket('users')

    b2['user1'] = {'name': 'mary'}

    assert b2.find({'name': 'mary'}) == ('user1', {'name': 'mary'})

Supported backends
==================

The following backends are supported by anykeystore:

pymongo
-------

Values are stored as MongoDB documents. Secondary indexes are stored inside the
MongoDB document itself and this backend is fairly fast::

    ks = anykeystore.MongoDB(host='localhost', port=27017, dbname='test')

sqlite3
-------

Values are json-encoded and stored in a table per bucket. Secondary indexes are
stored in a separate table. This backend is intended for development and not
production as it is not suitable for large amounts of data::

    ks = anykeystore.Sqlite(filename='keystore.db')

riak
----

Values are stored as Riak documents. Secondary indexes use Riak's secondary
indexes directly. Performance with this backend hasn't been well tested yet::

    ks = anykeystore.Riak(host='127.0.0.1', port=8098)

