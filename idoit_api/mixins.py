import logging

from functools import wraps
from idoit_api.const import LOG_LEVEL_DEBUG, LOG_LEVEL_INFO, LOG_LEVEL_WARNING, LOG_LEVEL_ERROR, LOG_PATH


class PermissionException(Exception):
    pass


class PermissionMixin:
    """This is a Mixin for permission management.

    If a class inherits from it you need to set PERMISSION_LEVEL to an integer via the __init__ method.
    Then the decorator check_permission_level can be used.

    It also provides decorators for function and method execution, that take a callback which must return a boolean.
    If the callback evaluates to true, that decorated function is executed

    ### Example ##########################################################
    class A(PermissionMixin):
        def __init__(self, required_permission_lvl):
            self.PERMISSION_LEVEL = required_permission_lvl or self.PERMISSION_LEVEL_1

        @PermissionMixin.check_permission_level(2)
        def write(self):
            print('wrote!')

    a = A(3)
    a.write()
    ######################################################################
    """

    DRY_RUN = 0
    PERMISSION_LEVEL_1 = 1
    PERMISSION_LEVEL_2 = 2
    PERMISSION_LEVEL_3 = 3
    PERMISSION_LEVEL_4 = 4
    PERMISSION_LEVEL_5 = 5

    PERMISSION_LEVEL = DRY_RUN

    @staticmethod
    def execute_condition(condition_func):
        """This decorator takes a condition function as argument that needs to return a boolean

        If the function evaluates to "True" the decorated function will be executed

        :param condition_func: Function or Lambda that returns a boolean
        :type condition_func: callable
        :return: wrapped function
        :rtype: object[function]
        """
        def conditional_excecution_decorator(func):
            @wraps(func)
            def wrapped_function(*args, **kwargs):
                if condition_func():
                    return func(*args, **kwargs)

            return wrapped_function

        return conditional_excecution_decorator

    @staticmethod
    def execute_condition_m(method_name):
        """This decorator takes a method name as argument that needs to return a boolean

        If the method evaluates to "True" the decorated function will be executed.

        :param method_name: Name of a method contained in class that returns a boolean
        :type method_name: str
        :return: wrapped method
        :rtype: object[function]
        """
        def conditional_excecution_decorator(method):
            @wraps(method)
            def inner(class_instance, *args, **kwargs):
                condition_method = getattr(class_instance, method_name)
                if condition_method():
                    return method(class_instance, *args, **kwargs)

            return inner
        return conditional_excecution_decorator

    @staticmethod
    def check_permission_level(required_permission_lvl, dry_run_allowed=False):
        """This decorator takes an integer or class constant (PERMISSION_LEVEL_1) and checks whether class method
        can be executed, by comparing required_permission_lvl to self.PERMISSION_LEVEL

        :param dry_run_allowed: Whether method can be run without actual execution aka. changes to any system or data
        :type dry_run_allowed: bool
        :param required_permission_lvl: PERMISSION_LEVEL required to allow execution of the decorated method
        :type required_permission_lvl: int
        :return: wrapped method
        :rtype: callable
        """
        # functions will get a permission level as decorator, to mark what permission is needed
        def method_decorator(method):
            @wraps(method)
            def inner(class_instance, *args, **kwargs):
                if int(class_instance.PERMISSION_LEVEL) >= int(required_permission_lvl):
                    return method(class_instance, *args, **kwargs)
                # TODO write dry_run decorator to re enable this functionality
                # elif dry_run_allowed and int(class_instance.PERMISSION_LEVEL) == PermissionMixin.DRY_RUN:
                #     print('dry running method: ', method)
                #     return method(class_instance, *args, **kwargs)
                else:
                    raise PermissionException(
                        'Permission level was not high enough to execute this function: {}.\n'
                        'Required permission level: {} --- current object permission level: {}'
                        ' Please check the documentation of PermissionMixin for details on how to avoid this error'
                        .format(
                            method,
                            required_permission_lvl,
                            class_instance.PERMISSION_LEVEL
                        ))
            return inner
        return method_decorator


class LoggingMixin(object):
    """Provides logging to all classes inheriting from this one"""

    def __init__(self, log_level=LOG_LEVEL_INFO,
                 log_path='{}/{}'.format(LOG_PATH, 'main.log'), *args, **kwargs):
        """Setup logging for class

        :param log_level: Set the log level
        :type log_level: int
        """

        self.log = logging.getLogger('{}.{}'.format(self.__module__, self.__class__.__name__))
        self.log_lvl = log_level
        self.log.setLevel(log_level)

        self._fh_log = logging.FileHandler(log_path)
        self._fh_log.setLevel(log_level)
        self._ch_log = logging.StreamHandler()
        self._ch_log.setLevel(logging.ERROR)

        self._formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s \n\t- %(message)s')
        self._fh_log.setFormatter(self._formatter)
        self._ch_log.setFormatter(self._formatter)

        self.log.addHandler(self._fh_log)
        self.log.addHandler(self._ch_log)



