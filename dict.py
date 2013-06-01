class DictBucket(dict):
    def __getitem__(self, key):
        return dict.get(self, key, None)

    def __delitem__(self, key):
        try:
            dict.__delitem__(self, key)
        except KeyError:
            pass

    def find(self, key):
        # TODO: implement find for dict
        raise NotImplementedError('Implement me!')

