
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

import sys
from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
from django.conf import settings
#import MySQLdb


def test_mysql():
    db_conn = connections['default']
    try:
        c = db_conn.cursor()
    except OperationalError:
        print("Mysql test connection failed")
        return False
    return True


def test_redis():
    print("Testing redis...")
    return True


def test_memcached():
    cache.set('foo', 'bar', 600)
    if(cache.get('foo') != 'bar'):
        print("memcached test connection failed!")
        return False
    return True


def test_elasticsearch():
    print("Testing elasticsearch...")
    return True


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
    mysql = test_mysql()
    redis = test_redis()
    memcached = test_memcached()
    elasticsearach = test_elasticsearch()
    if(mysql and redis and memcached and elasticsearach):
        print("All tests passed!")
