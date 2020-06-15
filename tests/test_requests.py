import pytest
import requests_mock

from idoit_api.requests import IdoitEndpoint, CMDBCategoryEndpoint
from idoit_api.exceptions import InvalidParams
from idoit_api.base import API
from tests.test_base import simple_param_dict


@pytest.fixture
def idoit_ep():
    yield IdoitEndpoint(api=API(url="https://cmdb.example.de"), permission_level=10, log_level=10)


@pytest.fixture
def category_ep():
    yield CMDBCategoryEndpoint(api=API(url="https://cmdb.example.de", log_level=10), permission_level=30)


class TestIdoitRequest:

    def test_init(self, idoit_ep):
        assert isinstance(idoit_ep, IdoitEndpoint)

    def test_properties(self, idoit_ep):
        with requests_mock.Mocker() as m:
            adapter = m.post(
                url="https://cmdb.example.de",
                json={'result': {'login':  {'userid': '9', 'name': 'admin ', 'mail': 'sample@mail.com', 'username': 'admin', 'tenant': 'Sample GmbH','language': 'en'},
                      'version': '1.14.2', 'step': '', 'type': 'PRO'}}
            )

            assert idoit_ep.version == '1.14.2'
            assert idoit_ep.version_type == 'PRO'
            assert idoit_ep.tenant == 'Sample GmbH'
            assert idoit_ep.user_id == '9'
            assert idoit_ep.mail == 'sample@mail.com'
            assert idoit_ep.language == 'en'


class TestCMDBCategoryEndpoint:

    def test_init(self, category_ep):
        assert isinstance(category_ep, CMDBCategoryEndpoint)

    def test_validate_request(self, simple_param_dict, category_ep):

        with pytest.raises(InvalidParams):
            category_ep.create()
        with pytest.raises(TypeError):
            category_ep.create({})
        with pytest.raises(InvalidParams):
            category_ep.create(**{'apikey': 'test'})
        with pytest.raises(InvalidParams):
            d = simple_param_dict.copy()
            del d['objID']
            category_ep.update(status="C__RECORD_STATUS__DELETED", **d)
        with pytest.raises(InvalidParams, match=r".* mutually exclusive required parameters .*"):
            d = simple_param_dict.copy()
            del d['category']
            category_ep.update(status="C__RECORD_STATUS__DELETED", **d)

        with requests_mock.Mocker() as m:
            result = {'entry': 5419, 'message': 'Category entry successfully saved', 'success': True}
            adapter = m.post(url="https://cmdb.example.de", json={"result": result})
            response = category_ep.create(**simple_param_dict)

            assert adapter.call_count == 1
            assert adapter.called

            assert adapter.last_request.json() == {
                'id': 0, # TODO update once we count up for requests
                'jsonrpc': '2.0',
                'method': 'cmdb.category.create',
                # TODO apikey is emtpty, find out why
                'params': {'apikey': '', 'category': 'C__CATS__APPLICATION', 'objID': 1455}
            }


