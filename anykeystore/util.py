import re

valid_name_re = re.compile('\w+')

def check_bucket_name(name):
    if valid_name_re.match(name) is None:
        raise ValueError('Invalid bucket name')
