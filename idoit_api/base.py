import requests

from abc import ABC, abstractmethod
from idoit_api.const import CATEGORY_CONST_MAPPING


class API(object):
    def __init__(self, url=None, key=None, username=None, password=None):
        """Base class for connecting to the JSON-RPC API

        :param url: URL to access the JSON-RPC API
        :type url: str
        :param key: API-Key
        :type key: str
        :param username: Username
        :type username: str
        :param password: Password
        :type password: str
        """
        self._session_id = None
        self.key = key
        self.username = username
        self.password = password
        self.url = url

    def login(self, username=None, password=None):
        """
        Perform login
        :param str username: Overrides the current username value
        :param str password: Overrides the current password value
        """
        if username:
            self.username = username
        if password:
            self.password = password

        headers = {
            "X-RPC-Auth-Username": self.username,
            "X-RPC-Auth-Password": self.password
        }

        result = self.request(
            "idoit.login",
            headers=headers
        )
        self._session_id = result["session-id"]

    def logout(self):
        self.request("idoit.logout")
        self._session_id = None

    def request(self, method, params=None, headers=None):
        """
        :param str method:
        :param dict params:
        :param dict headers:
        :return:
        """
        req_headers = {'content-type': 'application/json'}
        if self._session_id is not None:
            req_headers["X-RPC-Auth-Session"] = self._session_id

        if isinstance(headers, dict):
            req_headers.update(headers)

        req_params = {
            "apikey": self.key
        }
        if isinstance(params, dict):
            req_params.update(params)

        data = {
            "method": method,
            "params": req_params,
            "jsonrpc": "2.0",
            "id": 0,
        }

        response = requests.post(
            self.url,
            json=data,
            headers=req_headers
        ).json()

        if "error" in response:
            error = response["error"]
            error_code = error["code"]
            from idoit_api.exceptions import InvalidParams, InternalError, MethodNotFound, UnknownError
            for exception_class in [InvalidParams, InternalError, MethodNotFound]:
                if exception_class.code == error_code:
                    raise exception_class(
                        data=error["data"],
                        raw_code=error_code
                    )
            raise UnknownError(
                data=error["data"],
                raw_code=error_code
            )
        return response['result']


class RestObject(ABC):

    def __init__(self, data):
        self._raw_data = data
        # populate attributes from json dict
        self.populate()

        super().__init__()

    def populate(self, data=None):
        """Set object values from data dict

        :param data: dictionary of json data from API
        :type data: dict
        """
        data = data or self._raw_data

        if not data:
            raise AttributeError('cannot set attributes, param data and attribute self._raw_data were empty ')

        for k, v in data.items():
            self.__dict__[k] = v
        self._populate_custom()

    @abstractmethod
    def _populate_custom(self, data=None):
        """Implement this method in inherited class, to add object specific attributes"""
        pass


class CMDBDocument(RestObject):

    CATEGORY_MAP = CATEGORY_CONST_MAPPING

    def populate(self, data=None):
        """Set object values from data dict

        :param data: dictionary of json data from API
        :type data: dict
        """
        data = data or self._raw_data

        if not data:
            raise AttributeError('cannot set attributes, param data and attribute self._raw_data were empty ')

        for k, v in data.items():
            if k in self.CATEGORY_MAP:
                k = self.CATEGORY_MAP.get(k)
            self.__dict__[k] = v
        self._populate_custom()

    def _populate_custom(self, data=None):
        pass


class CMDBSoftwareAssignment(CMDBDocument):
    pass


class CMDBRelation(CMDBDocument):
    """Represents a relation from the CMDB"""
    pass


class CMDBCustomType(CMDBDocument):
    """Represents a custom object from the CMDB"""
    pass


class BaseRequest(object):
    def __init__(self, api=None, api_params=None):
        if api is None:
            if api_params is None:
                api_params = {}
            api = API(**api_params)
        self._api = api


class Idoit(BaseRequest):
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

    def search(self, query):
        return self._api.request(
            "idoit.search",
            {"q": query}
        )


class CMDBCategory(BaseRequest):
    STATUS_NORMAL = "C__RECORD_STATUS__NORMAL"
    STATUS_ARCHIVED = "C__RECORD_STATUS__ARCHIVED"
    STATUS_DELETED = "C__RECORD_STATUS__DELETED"

    def __init__(self, api=None, api_params=None, default_read_status=STATUS_NORMAL):
        super(CMDBCategory, self).__init__(api=api, api_params=api_params)
        self.default_read_status = default_read_status

    def read(self, object_id, category=None, catg_id=None, cats_id=None, status=None):
        """
        Read one or more category entries for an object.
        Use only one of the optional parameters category, catg_id or cats_id.
        :param int object_id: Object identifier
        :param str category: Category constant
        :param int catg_id: Global category identifier
        :param int cats_id: Specific category identifier
        :return: List of result objects
        :rtype: dict[]
        """
        params = {
            "objID": object_id
        }
        if category:
            params["category"] = category
        elif catg_id:
            params["catgID"] = catg_id
        elif cats_id:
            params["catsID"] = cats_id
        else:
            raise Exception("Missing parameter")

        if status is None:
            status = self.default_read_status
        if status is not None:
            params["status"] = status

        return self._api.request(
            method="cmdb.category.read",
            params=params
        )
