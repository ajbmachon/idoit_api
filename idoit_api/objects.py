from idoit_api.base import BaseEndpoint, MultiResultEndpoint, CMDBDocument
from idoit_api.const import NORMAL_SEARCH


class IdoitEndpoint(BaseEndpoint):

    @property
    def version(self):
        data = self.get_version()
        return data.get("version")

    @property
    def version_type(self):
        data = self.get_version()
        return data.get("type")

    @property
    def username(self):
        data = self.get_version()
        return data.get('login', {}).get('username')

    @property
    def tenant(self):
        data = self.get_version()
        return data.get('login', {}).get('tenant')

    @property
    def user_id(self):
        data = self.get_version()
        return data.get('login', {}).get('userid')

    @property
    def mail(self):
        data = self.get_version()
        return data.get('login', {}).get('mail')

    @property
    def language(self):
        data = self.get_version()
        return data.get('login', {}).get('language')

    def get_constants(self):
        return self._api.request("idoit.constants")

    def get_version(self):
        return self._api.request("idoit.version")

    def search(self, query, mode=NORMAL_SEARCH):
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

    def __init__(self, api=None, default_read_status=STATUS_NORMAL, **kwargs):
        super().__init__(api=api, **kwargs)

        self.REQUIRED_PARAMS.update(super().REQUIRED_PARAMS)
        self.default_read_status = default_read_status


#######################################################################
############################### OBJECTS ###############################
#######################################################################


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
