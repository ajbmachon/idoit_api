from idoit_api.base import RestObject
from idoit_api.const import CATEGORY_CONST_MAPPING


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
