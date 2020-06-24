from idoit_api.base import BaseEndpoint, MultiResultEndpoint, CMDBDocument
from idoit_api.const import *


# ##################################################################### #
# ############################## Endpoints ############################ #
# ##################################################################### #


class IdoitEndpoint(BaseEndpoint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._version_data = None
        self._constants_data = None

    @property
    def version(self):
        if not self._version_data:
            self.get_version()
        return self._version_data.get("version")

    @property
    def version_type(self):
        if not self._version_data:
            self.get_version()
        return self._version_data.get("type")

    @property
    def username(self):
        if not self._version_data:
            self.get_version()
        return self._version_data.get('login', {}).get('username')

    @property
    def tenant(self):
        if not self._version_data:
            self.get_version()
        return self._version_data.get('login', {}).get('tenant')

    @property
    def user_id(self):
        if not self._version_data:
            self.get_version()
        return self._version_data.get('login', {}).get('userid')

    @property
    def mail(self):
        if not self._version_data:
            self.get_version()
        return self._version_data.get('login', {}).get('mail')

    @property
    def language(self):
        if not self._version_data:
            self.get_version()
        return self._version_data.get('login', {}).get('language')

    def get_constants(self):
        self._constants_data = self._api.request("idoit.constants")
        return self._constants_data

    def get_version(self):
        self._version_data = self._api.request("idoit.version")
        return self._version_data

    def search(self, query, mode=NORMAL_SEARCH):
        return self._api.request(
            "idoit.search",
            {"q": query, "mode": mode}
        )


class CMDBObjectsEndpoint(MultiResultEndpoint):

    ENDPOINT = "cmdb.objects"


class CMDBCategoryEndpoint(BaseEndpoint):
    ENDPOINT = "cmdb.category"

    REQUIRED_PARAMS = {}
    REQUIRED_INTERCHANGEABLE_PARAMS = {
        ('category', 'catg_id', 'cats_id'): ('create', 'read', 'update')
    }
    OPTIONAL_PARAMS = {
        'status': ('read', 'update')
    }

    STATUS_NORMAL = "C__RECORD_STATUS__NORMAL"
    STATUS_ARCHIVED = "C__RECORD_STATUS__ARCHIVED"
    STATUS_DELETED = "C__RECORD_STATUS__DELETED"

    def __init__(self, api=None, default_read_status=STATUS_NORMAL, **kwargs):
        super().__init__(api=api, **kwargs)

        # Get Parameters from super class BaseEndpoint
        self.REQUIRED_PARAMS.update(super().REQUIRED_PARAMS)
        self.default_read_status = default_read_status


# ##################################################################### #
# ############################ CMDB TYPES ############################# #
# ##################################################################### #


class CMDBSoftwareAssignment(CMDBDocument):
    """Represents a software assignment"""
    pass


class CMDBRelation(CMDBDocument):
    """Represents a relation from the CMDB"""
    pass


class CMDBCustomType(CMDBDocument):
    """Represents a custom object from the CMDB"""
    pass


class CMDBCategoryEntry(CMDBDocument):
    """Represents an entry in a Category"""
    pass
