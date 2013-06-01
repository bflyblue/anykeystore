import riak
from util import check_bucket_name

class RiakBucket:
    def __init__(self, connection, name, indexfn=None):
        self.connection = connection
        self.name = name
        self.indexfn = indexfn
        self.bucket = self.connection.bucket(self.name)

    def get(self, key, default=None):
        key = str(key)
        o = self.bucket.get(key)
        if o.exists():
            return o.get_data()
        return default

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        key = str(key)
        o = self.bucket.new(key, value)
        if self.indexfn:
            for index, val in self.indexfn(key, value):
                o.add_index(str(index) + '_bin', str(val))
        o.store()

    def __delitem__(self, key):
        key = str(key)
        o = self.bucket.get(key)
        if o.exists():
            o.delete()

    def find(self, spec):
        results = []
        for i, (index, val) in enumerate(spec.items):
            keys = set([l.get_key() for l in self.connection.index(self.name, str(index) + '_bin', str(val)).run()])
            if i == 0:
                results = keys
            else:
                results.intersection_update(keys)
            if not results:
                break

        for key in results:
            yield key, self[key]

    def keys(self):
        for key in self.bucket.get_keys():
            if self[key] is not None:
                yield key

    def items(self):
        for key in self.bucket.get_keys():
            val = self[key]
            if val is not None:
                yield key, val

class Riak:
    def __init__(self, host='127.0.0.1', port=8098):
        self.connection = riak.RiakClient(host, port)

    def bucket(self, name, indexfn=None):
        check_bucket_name(name)
        return RiakBucket(self.connection, name, indexfn)
