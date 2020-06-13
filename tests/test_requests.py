import pytest
import requests_mock

from idoit_api.requests import IdoitEndpoint, CMDBCategoryEndpoint
from idoit_api.exceptions import InvalidParams
from idoit_api.base import API
from tests.test_base import simple_param_dict


class TestIdoitRequest:
    pass


class TestCMDBCategoryRequest:

    def test_init(self):
        r = CMDBCategoryEndpoint(api=API(url="https://cmdb.example.de", log_level=10))
        assert isinstance(r, CMDBCategoryEndpoint)

    def test_validate_request(self, simple_param_dict):
        r = CMDBCategoryEndpoint(api=API(url="https://cmdb.example.de", log_level=10, ), permission_level=3)

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
