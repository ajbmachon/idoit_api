import os

from idoit_api.base import BaseEndpoint, MultiResultEndpoint
from idoit_api.const import NORMAL_SEARCH, DEEP_SEARCH, AUTO_DEPP_SEARCH


class IdoitEndpoint(BaseEndpoint):

    @property
    def version(self):
        data = self.get_version()
        return data.get("version")

    @property
    def version_type(self):
        data = self.get_version()
        return data.get("type")

    def get_constants(self):
        return self._api.request("idoit.constants")

    def get_version(self):
        return self._api.request("idoit.version")

    def search(self, query, mode=NORMAL_SEARCH):
        self.log.debug(' ENVENVENVNEV %s %s ', os.environ.get('CMDB_USER'), os.environ.get('CMDB_PASS'))
        self.log.debug('IN IDOITENDPOINT %s %s %s', self._api.username, self._api.password, self.__class__)
        return self._api.request(
            "idoit.search",
            {"q": query, "mode": mode}
        )


class CMDBObjectsEndpoint(MultiResultEndpoint):

    ENDPOINT = "cmdb.objects"


class CMDBCategoryEndpoint(BaseEndpoint):
    ENDPOINT = "cmdb.category"

    STATUS_NORMAL = "C__RECORD_STATUS__NORMAL"
    STATUS_ARCHIVED = "C__RECORD_STATUS__ARCHIVED"
    STATUS_DELETED = "C__RECORD_STATUS__DELETED"

    REQUIRED_PARAMS = {}
    REQUIRED_INTERCHANGEABLE_PARAMS = {
        ('category', 'catg_id', 'cats_id'): ('create', 'read', 'update')
    }
    OPTIONAL_PARAMS = {
        'status': ('read', 'update')
    }

    def __init__(self, api=None, api_params=None, default_read_status=STATUS_NORMAL, **kwargs):
        super().__init__(api=api, api_params=api_params, **kwargs)

        self.REQUIRED_PARAMS.update(super().REQUIRED_PARAMS)
        self.default_read_status = default_read_status
