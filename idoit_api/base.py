import requests
import os

from abc import ABC
from functools import partial

from autoslot import SlotsMeta

from idoit_api.const import *
from idoit_api.const import CATEGORY_CONST_MAPPING
from idoit_api.mixins import LoggingMixin, PermissionMixin
from idoit_api.exceptions import InvalidParams, InternalError, MethodNotFound, UnknownError, AuthenticationError


class API(LoggingMixin):
    """Provides functionality for authentication and generic requests against the idoit JSON-RPC API"""

    @property
    def key(self):
        return self._key or os.environ.get('CMDB_API_KEY', "")

    @key.setter
    def key(self, value):
        self._key = value
        os.environ['CMDB_API_KEY'] = value

    @property
    def session_id(self):
        return self._session_id or os.environ.get('CMDB_SESSION_ID', "")

    @session_id.setter
    def session_id(self, value):
        self._session_id = value
        os.environ['CMDB_SESSION_ID'] = value

    @property
    def url(self):
        return self._url or os.environ.get("CMDB_URL", "")

    @url.setter
    def url(self, value):
        self._url = value
        os.environ['CMDB_URL'] = value

    @property
    def username(self):
        return self._username or os.environ.get('CMDB_USER', "")

    @username.setter
    def username(self, value):
        self._username = value
        os.environ['CMDB_USER'] = value

    @property
    def password(self):
        return self._password or os.environ.get('CMDB_PASS', "")

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

        self._key = None
        self._session_id = None
        self._url = None
        self._username = None
        self._password = None

        # try to get credentials from environment if none are passed here
        self.key = key or self.key
        self.session_id = self.session_id
        self.url = url or self.url
        self.username = username or self.username
        self.password = password or self.password

        super().__init__(*args, **kwargs)

    def login(self, username=None, password=None):
        """Obtains session ID from the CMDB if none is set, by logging in with username and password

        :param username: Overrides the current username value
        :type username: str
        :param password: Overrides the current password value
        :type password: str
        """

        if self.session_id:
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
        self.log.debug('result of login: ' % result)
        self.session_id = result["session-id"]
        return True

    def logout(self):
        self.request("idoit.logout")
        self.session_id = None
        return True

    def request(self, method, params=None, headers=None):
        """Sends a POST request with JSON body to specified URL

        :param method: API method / endpoint to target
        :type method: str
        :param params: Extra key: value attributes for the JSON body
        :type params: dict
        :param headers: Extra headers to be sent with the request
        :type headers: dict
        :raises: AuthenticationError, InvalidParams, InternalError, MethodNotFound, UnknownError
        :return: dictionary with results from CMDB JSON API
        :rtype: dict
        """
        self.log.debug('parameters passed to request - method: %s, params: %s, headers: %s', method, params, headers)

        self.log.debug('API attributes username: %s  key: %s, pw: %s', self.username, self.key, self.password)

        request_content = {
            "url": self.url,
            "json": self.build_request_body(method, params),
            "headers": self._build_request_headers(headers)
        }

        self.log.debug('Request to be sent: %s', request_content)
        # self.log.info('Request to be sent: %s', request_content)

        response = requests.post(
            **request_content
        ).json()

        response = self._evaluate_response(response)
        return response['result']

    def batch_request(self, request_dicts):
        """Performs multiple requests to API at once

        :param request_dicts:
        :return:
        """

        data = []
        for rd in request_dicts:
            if rd.get('method') and rd.get('params') and rd.get('apikey') and rd.get('jsonrpc') and rd.get('id'):
                data.append(rd)

        response = requests.post(url=self.url, json=data, headers=self._build_request_headers({}))
        results = []
        # TODO check if this is possible
        for r in response.json():
            try:
                self._evaluate_response(r)
                results.append(r.get('result'))
            except (InvalidParams, InternalError, MethodNotFound, UnknownError, AuthenticationError) as err:
                print(err)

        return results

    def build_request_body(self, method, params=None):
        if not isinstance(method, str):
            raise AttributeError("Invalid api method passed to _build_request_body")

        params = params or {}
        params["apikey"] = self.key
        return {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            # TODO count up from class parameter here self._id += 1
            "id": 0,
        }

    def _build_request_headers(self, headers=None):

        h = headers or {}
        h['content-type'] = 'application/json'
        if self.session_id:
            h["X-RPC-Auth-Session"] = self.session_id
        else:
            h["X-RPC-Auth-Username"] = self.username
            h["X-RPC-Auth-Password"] = self.password
        return h

    def _evaluate_response(self, response):
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
        return response


class BaseEndpoint(ABC, PermissionMixin, LoggingMixin):
    """Base class for all Endpoints

    Subclasses need to define the parameters their CRUD operations expect and their API method.
    This is done by filling the following class constants, which are also used to document the
    parameters of API call methods and the Endpoint.

    'ENDPOINT'                        -> holds the API method.
    'REQUIRED_PARAMS'                 -> Keys are required parameters for the request, values is a tuple of which API
                                         method they apply to. Or 'True' in case they apply to all of them.
    'REQUIRED_INTERCHANGEABLE_PARAMS' -> Keys are a tuple of parameters for the request, of which are required if the
                                         others are missing. values are like in REQUIRES_PARAMS.
    'OPTIONAL_PARAMS'                 -> Keys are API call methods, values is a tuple of optional parameters, these are
                                         not checked as of now, but used for documentation purposes.
    'API_METHODS'                     -> Method names of all methods that interact with the idoit JSON-RPC API

    Example:
        ENDPOINT = "cmdb.category"
        REQUIRED_PARAMS = {'objID': ('read', 'update', 'delete'), 'category': True}
        REQUIRED_INTERCHANGEABLE_PARAMS = {('category', 'catgID', 'catsID'): True}
        OPTIONAL_PARAMS = {'update': ('title', 'version', 'assignments') }
        API_METHODS = ('create', 'read', 'update', 'delete', 'save', 'batch_update')

    """

    ENDPOINT = ""
    REQUIRED_PARAMS = {'objID': ('read', 'update', 'delete')}
    REQUIRED_INTERCHANGEABLE_PARAMS = {}
    OPTIONAL_PARAMS = {}
    API_METHODS = ('create', 'read', 'update', 'delete')

    SORT_ASCENDING = 'ASC'
    SORT_DESCENDING = 'DESC'

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log.debug('Created Endpoint: %s', self.__class__.__name__)

        if api is None:
            api = API(**kwargs)
        self._api = api
        self.PERMISSION_LEVEL = kwargs.get('permission_level', 1)

    def __str__(self):
        s = """{class_name}

        API METHOD TARGET: {endpoint}

        API METHOD SIGNATURES:
        """.format(
            class_name=self.__class__,
            endpoint=self.ENDPOINT
        )

        for method, pd in self._gen_api_method_signature().items():
            s = """{s}
            {method}()
              REQUIRED        : {req}
              INTERCHANGEABLE : {intc}
              OPTIONAL        : {opt}
            """.format(s=s, method=method, req=pd.get('required'),
                       intc=pd.get('interchangeable'), opt=pd.get('optional'))
        return s

    def __getattribute__(self, item):
        if item in ('create', 'read', 'update', 'delete', 'save', 'batch_update'):
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
        if 'obj' in kwargs and issubclass(kwargs.get('obj').__class__, CMDBDocument):
            kwargs.update(self._build_request_dict_from_obj(kwargs.get('obj')))

        self.log.debug('Parameters passed to _validate_request: %s', kwargs)
        print('Parameters passed to _validate_request: ', kwargs)

        for param, rules in self.REQUIRED_PARAMS.items():
            if isinstance(rules, tuple):
                # check if rule is applicable for this method
                for method_name in rules:
                    if method.__name__ is not method_name:
                        continue
                    if param not in kwargs or kwargs.get(param, None) is None:
                        raise InvalidParams(message="Required parameter: {} is missing!".format(param))
            # rule is applicable to all API methods
            elif rules is True:
                if param not in kwargs or kwargs.get(param, None) is None:
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
                            if key in kwargs and kwargs.get(key, None) is not None:
                                found_key = True
                        if not found_key:
                            raise InvalidParams(
                                message="None of the mutually exclusive required parameters were passed: ".format(
                                    params)
                            )

        return method(**{k: v for k, v in kwargs.items() if v is not None})

    def _build_request_dict_from_obj(self, obj):
        d = {}
        for key in self.REQUIRED_PARAMS.keys():
            d[key] = obj.__dict__.get(key)
        for keys in self.REQUIRED_INTERCHANGEABLE_PARAMS.keys():
            for key in keys:
                d[key] = obj.__dict__.get(key)
        for key in self.OPTIONAL_PARAMS.keys():
            d[key] = obj.__dict__.get(key)
        return d

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

    def _gen_api_method_signature(self):
        """Maps all API methods to their parameters

        :return: Dict of dicts, keys are methods names, values are dicts which specify parameters
        :rtype: dict
        """

        methods = {}
        for m in self.API_METHODS:
            methods[m] = {
                'required': [],
                'interchangeable': [],
                'optional': []
            }
        # add all required params
        for param, ms in self.REQUIRED_PARAMS.items():
            if isinstance(ms, bool):
                for val in methods.values():
                    m_req = val.get('required', [])
                    if param not in m_req:
                        m_req.append(param)
            else:
                for m in ms:
                    m_req = methods.get(m, {}).get('required', [])
                    if param not in m_req:
                        m_req.append(param)
        # add all params of which only one in the set must be present
        for params, ms in self.REQUIRED_INTERCHANGEABLE_PARAMS.items():
            if isinstance(ms, bool):
                for val in methods.values():
                    m_req_i = val.get('interchangeable', [])
                    m_req_i.extend([p for p in params if p not in m_req_i])
            else:
                for m in ms:
                    m_req_i = methods.get(m, {}).get('interchangeable', [])
                    m_req_i.extend([p for p in params if p not in m_req_i])
        # add all optional params
        for m, params in self.OPTIONAL_PARAMS.items():
            m_opt = methods.get(m, {}).get('optional', [])
            m_opt.extend([p for p in params if p != True and p not in m_opt])

        return methods

    @PermissionMixin.check_permission_level(
        CREATE_ENTRIES, )  # TODO set dry_run_allowed=True after writing  dry run decorator
    def _create(self, **kwargs):
        return self._api.request(
            method=self.ENDPOINT + ".create",
            params=self._build_request_body(**kwargs)
        )

    @PermissionMixin.check_permission_level(READ_DATA, )
    def _read(self, **kwargs):
        return self._api.request(
            method=self.ENDPOINT + ".read",
            params=self._build_request_body(**kwargs)
        )

    @PermissionMixin.check_permission_level(UPDATE_ENTRIES, )
    def _update(self, **kwargs):
        return self._api.request(
            method=self.ENDPOINT + ".update",
            params=self._build_request_body(**kwargs)
        )

    @PermissionMixin.check_permission_level(UPDATE_ENTRIES, )
    def _save(self, **kwargs):
        return self._api.request(
            method=self.ENDPOINT + ".save",
            params=self._build_request_body(**kwargs)
        )

    @PermissionMixin.check_permission_level(DELETE_ENTRIES, )
    def _delete(self, **kwargs):
        return self._api.request(
            method=self.ENDPOINT + ".delete",
            params=self._build_request_body(**kwargs)
        )

    def create(self, **kwargs):
        return self._create(**kwargs)

    def read(self, **kwargs):
        return self._read(**kwargs)

    def update(self, **kwargs):
        return self._update(**kwargs)

    def delete(self, **kwargs):
        return self._delete(**kwargs)


class MultiResultEndpoint(BaseEndpoint):
    # TODO implement!
    pass


class CMDBDocument():

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raw_data = data.copy()

        self._populate(data)
        self._populate_custom(data)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._raw_data)

    def _populate(self, data=None):
        """Set object values from data dict

        :param data: dictionary of json data from API
        :type data: dict
        """
        data = data or self._raw_data

        if not data:
            raise AttributeError('cannot set attributes, param data and attribute self._raw_data were empty ')

        for k, v in data.items():
            # TODO move this into subclass and let this class assign all values. This is an entry. Other classes will start by building categories and filling them with entries
            # if k in self.CATEGORY_MAP:
            #     k = self.CATEGORY_MAP.get(k)
            # self.__dict__[k] = v
            self.__dict__[k] = v
        self._populate_custom()

    def _populate_custom(self, data=None):
        pass


class CMDBObjectTypeGroup:
    pass


class CMDBObject(metaclass=SlotsMeta):
    """Through its metaclass CMDBObject converts attributes defined in __init__() to the __slots__ attribute

    This is to save memory for the thousands of object that will be created from large requests.
    It can be subclassed like below. All subclasses should call super().__init__(title=title).


    Example:
         class Plugin(CMDBObject):
             def __init__(self, title, plugin_id):
                 self.plugin_id = plugin_id
                 super().__init__(title=title)

         class UIPlugin(Plugin):
             def __init__(self, title, plugin_id, template='default_template'):
                 self.template = template
                 super().__init__(title=title, plugin_id=plugin_id)
    """

    def __init__(self, title):
        """
        :param title: Object Title - The title is documented as an attribute in the "General" category.
                      This attribute is synonymously also called "Name" or "Object link".
        :type title: str
        """
        self.title = title
    pass


class CMDBCategory:
    pass


class CMDBAttribute:
    """
    TODO validation for different types of fields
        - single-line
        - multi-line
        - date field
        - html editor
        - FIND OUT THE OTHER RELEVANT ONES
    """

    def __init__(self, mandatory=False, custom_validator=False):
        pass
    pass

class CMDBObjectType(LoggingMixin):
    CATEGORY_MAP = CATEGORY_CONST_MAPPING

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raw_data = data.copy()
        self._populate_categories(data)

    def _populate_categories(self, data=None):
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
