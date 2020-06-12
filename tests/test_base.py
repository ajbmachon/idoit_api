import pytest
import os

import requests_mock
from idoit_api.base import API, CMDBDocument, BaseRequest, IdoitRequest, CMDBCategoryRequest
from idoit_api.const import CATEGORY_CONST_MAPPING
from idoit_api.exceptions import InvalidParams
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
        a = API(url="https://cmdb.example.de", log_lvl=10)
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


class TestCMDBCategoryRequest:

    def test_init(self):
        r = CMDBCategoryRequest(api=API(url="https://cmdb.example.de", log_lvl=10))
        assert isinstance(r, CMDBCategoryRequest)

    def test_validate_request(self, simple_param_dict):
        r = CMDBCategoryRequest(api=API(url="https://cmdb.example.de", log_lvl=10))

        with pytest.raises(InvalidParams):
            r.create()
        with pytest.raises(TypeError):
            r.create({})
        with pytest.raises(InvalidParams):
            r.create(**{'apikey': 'test'})
        with pytest.raises(InvalidParams):
            d = simple_param_dict.copy()
            del d['objID']
            r.create(status="C__RECORD_STATUS__DELETED", **d)
        with pytest.raises(InvalidParams, match=r".* mutually exclusive required parameters .*"):
            d = simple_param_dict.copy()
            del d['category']
            r.create(status="C__RECORD_STATUS__DELETED", **d)

        with requests_mock.Mocker() as m:
            result = {'entry': 5419, 'message': 'Category entry successfully saved', 'success': True}
            m.post(url="https://cmdb.example.de", json={"result": result})
            response = r.create(**simple_param_dict)
            assert response == result


class TestIdoit:
    pass


class TestCMDB:
    pass
