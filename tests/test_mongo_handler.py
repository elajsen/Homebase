import pytest
import json
from Homebase.models.mongo_handler import MongoHandler
from django.conf import settings


def get_credentials():
    with open("Homebase/credentials.conf") as f:
        return json.load(f)


def setUp():
    settings.configure()
    settings.CREDENTIALS = get_credentials()


def test_mongo_connection():
    setUp()
    mh = MongoHandler()
    try:
        res = mh.list_databases()
        print(res)
        assert True
    except:
        assert False
