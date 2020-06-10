import pytest
from idoit_api.base import API, CMDBDocument, BaseRequest, Idoit, CMDBCategory


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


class TestCMDBDocument:

    def test_populate(self, get_generic_json_dict):
        o = CMDBDocument(data=get_generic_json_dict)

        for k, v in get_generic_json_dict.items():
            assert o.__dict__[k] == v


