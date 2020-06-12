import json

import pytest
import requests

import requests_mock
from idoit_api.base import API, CMDBDocument, BaseRequest, IdoitRequest, CMDBCategoryRequest
from idoit_api.const import CATEGORY_CONST_MAPPING
from idoit_api.exceptions import InvalidParams


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


class TestCMDBDocument:

    def test_populate(self, get_generic_json_dict):
        o = CMDBDocument(data=get_generic_json_dict)

        for k, v in get_generic_json_dict.items():
            assert o.__dict__[k] == v


class TestAPI:
    """
    Class Docstring
    """

    def test_init(self):
        o = API(url="https://cmdb.qualitus.de", log_lvl=10)
        assert isinstance(o, API)


class TestCMDBCategoryRequest:

    def test_init(self):
        r = CMDBCategoryRequest(api=API(url="https://cmdb.qualitus.de", log_lvl=10))
        assert isinstance(r, CMDBCategoryRequest)

    def test_validate_request(self, simple_param_dict):
        r = CMDBCategoryRequest(api=API(url="https://cmdb.qualitus.de", log_lvl=10))

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

        with requests_mock.Mocker() as m:
            result = {'entry': 5419, 'message': 'Category entry successfully saved', 'success': True}
            m.post(url="https://cmdb.qualitus.de", json={"result": result})
            response = r.create(**simple_param_dict)
            assert response == result


class TestIdoit:
    pass


class TestCMDB:
    pass
