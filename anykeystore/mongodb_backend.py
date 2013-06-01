import pymongo
from util import check_bucket_name

# Retry function if pymongo needs to reconnect
# After 'times' retries it reraises original exception
def retry(times=3):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            retry = 0
            while retry < times:
                try:
                    result = fn(*args, **kwargs)
                except pymongo.errors.AutoReconnect:
                    retry += 1
                else:
                    break
            else:
                raise
            return result
        return wrapper
    return decorator

class MongoBucket:
    RETRY_LIMIT = 3

    def __init__(self, collection, indexfn=None):
        self.collection = collection
        self.indexfn = indexfn

    @retry(RETRY_LIMIT)
    def get(self, key, default=None):
        key = str(key)
        o = self.collection.find_one({'key': key})
        if o is None:
            return default
        return o['value']

    def __getitem__(self, key):
        return self.get(key)

    @retry(RETRY_LIMIT)
    def __setitem__(self, key, value):
        key = str(key)
        doc = {'key': key, 'value': value}
        if self.indexfn:
            for index, val in self.indexfn(key, value):
                doc.setdefault('i_' + str(index), []).append(str(val))
                self.collection.ensure_index('i_' + index)
        self.collection.update({'key': key}, doc, upsert=True)

    @retry(RETRY_LIMIT)
    def __delitem__(self, key):
        key = str(key)
        self.collection.remove({'key': key})

    @retry(RETRY_LIMIT)
    def keys(self):
        docs = self.collection.find(fields=['key'])
        return (d['key'] for d in docs)

    @retry(RETRY_LIMIT)
    def items(self):
        docs = self.collection.find(fields=['key', 'value'])
        return ((d['key'], d['value']) for d in docs)

    @retry(RETRY_LIMIT)
    def find(self, spec):
        mspec = {}
        for k in spec:
            mspec['i_' + str(k)] = str(spec[k])
        docs = self.collection.find(mspec)
        return ((d['key'], d['value']) for d in docs)

class MongoDB:
    def __init__(self, host='localhost', port=27017, dbname='test'):
        self.connection = pymongo.Connection(host, port, auto_start_request=False)
        self.database = self.connection[dbname]

    def bucket(self, name, indexfn=None):
        check_bucket_name(name)
        return MongoBucket(self.database[name], indexfn)
