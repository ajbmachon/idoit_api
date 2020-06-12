import requests
import os

from abc import ABC, abstractmethod
from idoit_api.const import CATEGORY_CONST_MAPPING
from idoit_api.mixins import LoggingMixin
from idoit_api.exceptions import InvalidParams, InternalError, MethodNotFound, UnknownError, AuthenticationError
from functools import partial

# TODO refactor this file. API and subclasses should be used like factory methods, that create objects:
#   so instead of an active record pattern we have more of a repository pattern


class API(LoggingMixin):
    """Provides functionality for authentication and genereic requests against the idoit JSON-RPC API"""

    @property
    def key(self):
        return self._key or os.environ.get('CMDB_API_KEY')

    @key.setter
    def key(self, value):
        self._key = value
        os.environ['CMDB_API_KEY'] = value

    @property
    def session_id(self):
        return self._session_id or os.environ.get('CMDB_SESSION_ID')

    @session_id.setter
    def session_id(self, value):
        self._session_id = value
        os.environ['CMDB_SESSION_ID'] = value

    @property
    def url(self):
        return self._url or os.environ.get("CMDB_URL")

    @url.setter
    def url(self, value):
        self._url = value
        os.environ['CMDB_URL'] = value

    @property
    def username(self):
        return self._username or os.environ.get('CMDB_USER')

    @username.setter
    def username(self, value):
        self._username = value
        os.environ['CMDB_USER'] = value

    @property
    def password(self):
        return self._password or os.environ.get('CMDB_PASS')

    @password.setter
    def password(self, value):
        self._password = value
        os.environ['CMDB_PASS'] = value

    def __init__(self, url=None, key=None, username=None, password=None, *args, **kwargs):
        """Setup the attributes needed for requests and logging

        :param url: URL to access the JSON-RPC API
        :type url: str
        :param key: API-Key
        :type key: str
        :param username: Username
        :type username: str
        :param password: Password
        :type password: str
        """

        # try to get credentials from environment if none are passed here
        self.key = key or self.key
        self.session_id = os.environ.get('CMDB_SESSION_ID', None)
        self.url = url or self.url
        self.username = username or self.url
        self.password = password or self.url

        super().__init__(*args, **kwargs)

    def login(self, username=None, password=None):
        """Obtains session ID from the CMDB if none is set, by logging in with username and password

        :param username: Overrides the current username value
        :type username: str
        :param password: Overrides the current password value
        :type password: str
        """

        if self._session_id or os.environ.get("CMDB_SESSION_ID"):
            return True

        user = username or self.username
        pw = password or self.password

        if not user:
            raise AuthenticationError(
                message=" 'idoit.login' failed, no username was set and env var 'CMDB_USER' is empty!"
            )
        if not pw:
            raise AuthenticationError(
                message=" idoit.login' failed, no password was set and env var 'CMDB_PASS' is empty!"
            )

        headers = {
            "X-RPC-Auth-Username": user,
            "X-RPC-Auth-Password": pw
        }

        result = self.request(
            "idoit.login",
            headers=headers
        )
        self.session_id = result["session-id"]
        return True

    def logout(self):
        self.request("idoit.logout")
        self.session_id = None
        return True

    def request(self, method, params=None, headers=None, url=None):
        """Sends a POST request with JSON body to specified URL

        :param method: API method / endpoint to target
        :type method: str
        :param params: Extra key: value attributes for the JSON body
        :type params: dict
        :param headers: Extra headers to be sent with the request
        :type headers: dict
        :param url: URL to access the JSON-RPC API
        :type url: str
        :raises: AuthenticationError, InvalidParams, InternalError, MethodNotFound, UnknownError
        :return: dictionary with results from CMDB JSON API
        :rtype: dict
        """
        req_headers = {'content-type': 'application/json'}

        if self.session_id is None:
            self.login()

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
            url or self.url,
            json=data,
            headers=req_headers
        ).json()

        if "error" in response:
            error = response["error"]
            error_code = error["code"]

            for exception_class in [InvalidParams, InternalError, MethodNotFound]:
                if exception_class.code == error_code:
                    raise exception_class(
                        data=error["data"],
                        raw_code=error_code
                    )
            if error_code == AuthenticationError.code:
                self._session_id = None
                del os.environ['CMDB_SESSION_ID']
                raise AuthenticationError(
                    data=error["data"],
                    raw_code=error_code
                )

            raise UnknownError(
                data=error["data"],
                raw_code=error_code
            )
        return response['result']


class BaseRequest(object):
    # CMDB API Endpoint should be entered here, like: cmdb.category
    ENDPOINT = ""

    REQUIRED_PARAMS = {
        'objID': ('create', 'read', 'update', 'delete')
    }
    # Keys need to be tuples here and only be filles if there are mutually exclusive but required parameters
    REQUIRED_INTERCHANGEABLE_PARAMS = {}
    OPTIONAL_PARAMS = {}

    def __init__(self, api=None, api_params=None):
        if api is None:
            if api_params is None:
                api_params = {}
            api = API(**api_params)
        self._api = api

    def __getattribute__(self, item):
        if item in ('create', 'read', 'update', 'delete'):
            return partial(self._validate_request, method=object.__getattribute__(self, item))
        return object.__getattribute__(self, item)

    def _validate_request(self, method, **kwargs):
        """ Validates an API request body, based on constants defined in the class

        if required parameters are missing it throws the appropriate exception

        :param method: API CRUD class method to be validated
        :type method: callable
        :param kwargs: Parameters for method to be validated
        :raise: InvalidParams, AttributeError
        :return: passed method
        """
        if kwargs is None:
            raise InvalidParams(message="Please specify some parameters for the request")
        if not isinstance(kwargs, dict):
            raise InvalidParams(message="Parameters for the API call need to be a dictionary")

        for param, rules in self.REQUIRED_PARAMS.items():
            if isinstance(rules, tuple):
                # check if rule is applicable for this method
                for method_name in rules:
                    if method.__name__ is not method_name:
                        continue
                    if param not in kwargs:
                        raise InvalidParams(message="Required parameter: {} is missing!".format(param))
            # rule is applicable to all API methods
            elif rules is True:
                if param not in kwargs:
                    raise InvalidParams(message="Required parameter: {} is missing!".format(param))
            else:
                raise AttributeError("Your validation dictionary is malformed, values need to be a tuple or True")

            # check if none of mutually exclusive, but required params is present
            for params, rs in self.REQUIRED_INTERCHANGEABLE_PARAMS.items():
                if isinstance(rs, tuple):
                    for method_name in rs:
                        if method.__name__ is not method_name:
                            continue

                        found_key = False
                        for key in params:
                            if key in kwargs:
                                found_key = True
                        if not found_key:
                            raise InvalidParams(
                                message="None of the mutually exclusive required parameters were passed: ".format(params)
                            )

        return method(**kwargs)

    def _build_request_body(self, **kwargs):
        d = {}
        for k, v in kwargs.items():
            if k in self.REQUIRED_PARAMS or k in self.OPTIONAL_PARAMS:
                d[k] = v
            for keys in self.REQUIRED_INTERCHANGEABLE_PARAMS.keys():
                if k in keys:
                    d[k] = v
                    continue
        return d

    def create(self, **kwargs):
        print('received the following kwargs: ', kwargs)
        return self._api.request(
            method=self.ENDPOINT + ".create",
            params=self._build_request_body(**kwargs)
        )

    def read(self, **kwargs):
        return self._api.request(
            method=self.ENDPOINT + ".read",
            params=self._build_request_body(**kwargs)
        )

    def update(self, **kwargs):
        return self._api.request(
            method=self.ENDPOINT + ".update",
            params=self._build_request_body(**kwargs)
        )

    def delete(self, **kwargs):
        return self._api.request(
            method=self.ENDPOINT + ".delete",
            params=self._build_request_body(**kwargs)
        )


class IdoitRequest(BaseRequest):
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


class CMDBCategoryRequest(BaseRequest):
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

    def __init__(self, api=None, api_params=None, default_read_status=STATUS_NORMAL):
        super(CMDBCategoryRequest, self).__init__(api=api, api_params=api_params)

        self.REQUIRED_PARAMS.update(super().REQUIRED_PARAMS)
        self.default_read_status = default_read_status


class RestObject(LoggingMixin, ABC):

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
    """Represents a software assignment"""
    pass


class CMDBRelation(CMDBDocument):
    """Represents a relation from the CMDB"""
    pass


class CMDBCustomType(CMDBDocument):
    """Represents a custom object from the CMDB"""
    pass

