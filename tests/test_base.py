import pytest
import os

import requests_mock
from idoit_api.base import API, CMDBDocument, BaseEndpoint
from idoit_api.const import CATEGORY_CONST_MAPPING

from idoit_api.utils import set_env_credentials, del_env_credentials


@pytest.fixture
def get_generic_json_dict():
    return {
        'attribute_1': 1,
        'attribute_2': '2',
        'attribute_3': 3,
        'attribute_4': {
            'attribute_5': 5
        },
    }


@pytest.fixture
def simple_param_dict():
    return {
        'objID': 1455,
        'category': CATEGORY_CONST_MAPPING['application'],
        'apikey': 'test'
    }


class EnvCredentials:

    def __enter__(self):
        set_env_credentials("not_so_secret_account_name", "my_super_secret_password","cmdb_key_also_super_secret","https://cmdb.example.de/src/jsonrpc.php",)

    def __exit__(self, exc_type, exc_val, exc_tb):
        del_env_credentials()

    @staticmethod
    def set_session_id():
        os.environ['CMDB_SESSION_ID'] = "cmdb_session_id"


class TestCMDBDocument:

    def test_populate(self, get_generic_json_dict):
        o = CMDBDocument(data=get_generic_json_dict)

        for k, v in get_generic_json_dict.items():
            assert o.__dict__[k] == v


class TestAPI:

    def test_init(self):
        a = API(url="https://cmdb.example.de", log_level=10)
        assert isinstance(a, API)

    def test_properties(self):
        with EnvCredentials():
            a = API()
            assert a._username == os.environ['CMDB_USER']
            assert a._password == os.environ['CMDB_PASS']
            assert a._key == os.environ['CMDB_API_KEY']
            assert a._url == os.environ['CMDB_URL']

    def test_login(self):
        pass

    def test_logout(self):
        pass

    def test_request(self):
        pass


