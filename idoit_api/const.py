from pathlib import Path
from os.path import join

__all__ = [
    'CATEGORY_CONST_MAPPING',
    'LOG_PATH',
    'LOG_LEVEL_DEBUG',
    'LOG_LEVEL_INFO',
    'LOG_LEVEL_ERROR',
    'LOG_LEVEL_WARNING',
    'DRY_RUN',
    'READ_DATA',
    'READ_SENSITIVE_DATA',
    'CREATE_ENTRIES',
    'UPDATE_ENTRIES',
    'DELETE_ENTRIES',
    'NORMAL_SEARCH',
    'DEEP_SEARCH',
    'AUTO_DEPP_SEARCH',
    'STATUS_NORMAL',
    'STATUS_ARCHIVED',
    'STATUS_DELETED'
]

# LOGGING
LOG_PATH = join(str(Path.home()), '.idoit_api')
LOG_LEVEL_DEBUG = 10
LOG_LEVEL_INFO = 20
LOG_LEVEL_ERROR = 30
LOG_LEVEL_WARNING = 40

# APP PERMISSION
DRY_RUN = 0
READ_DATA = 10
READ_SENSITIVE_DATA = 20
CREATE_ENTRIES = 30
UPDATE_ENTRIES = 40
DELETE_ENTRIES = 50

# SEARCH ALGORITHM TYPE
NORMAL_SEARCH = 'normal'
DEEP_SEARCH = 'deep'
AUTO_DEPP_SEARCH = 'auto-deep'

# RECORD STATUS
STATUS_NORMAL = "C__RECORD_STATUS__NORMAL"
STATUS_ARCHIVED = "C__RECORD_STATUS__ARCHIVED"
STATUS_DELETED = "C__RECORD_STATUS__DELETED"

# Mapping of category constants to more readable names
CATEGORY_CONST_MAPPING = {
    'application': 'C__CATS__APPLICATION', 'it_service': 'C__CATG__IT_SERVICE',
    'version': 'C__CATG__VERSION', 'relation': 'C__CATG__RELATION',
    'planning': 'C__CATG__PLANNING', 'global': 'C__CATG__GLOBAL', 'contact': 'C__CATG__CONTACT',
    'software_assignment': 'C__CATG__APPLICATION',
    'application_assigned_obj': 'C__CATS__APPLICATION_ASSIGNED_OBJ',
    'application_variant': 'C__CATS__APPLICATION_VARIANT',
    'cluster_service': 'C__CATG__CLUSTER_SERVICE', 'backup': 'C__CATG__BACKUP',
    'cluster_memberships': 'C__CATG__CLUSTER_MEMBERSHIPS',
    'power_consumer': 'C__CATG__POWER_CONSUMER', 'network_port': 'C__CATG__NETWORK_PORT',
    'location': 'C__CATG__LOCATION', 'universal_interface': 'C__CATG__UNIVERSAL_INTERFACE',
    'ip': 'C__CATG__IP', 'controller_fc_port': 'C__CATG__CONTROLLER_FC_PORT',
    'connector': 'C__CATG__CONNECTOR', 'ldev_client': 'C__CATG__LDEV_CLIENT',
    'group_memberships': 'C__CATG__GROUP_MEMBERSHIPS',
    'person_assigned_groups': 'C__CATS__PERSON_ASSIGNED_GROUPS',
    'database_access': 'C__CATS__DATABASE_ACCESS', 'database_links': 'C__CATS__DATABASE_LINKS',
    'database_gateway': 'C__CATS__DATABASE_GATEWAY',
    'database_schema': 'C__CATS__DATABASE_SCHEMA',
    'it_service_components': 'C__CATG__IT_SERVICE_COMPONENTS',
    'replication_partner': 'C__CATS__REPLICATION_PARTNER',
    'soa_components': 'C__CATG__SOA_COMPONENTS', 'soa_stacks': 'C__CATG__SOA_STACKS',
    'database_instance': 'C__CATS__DATABASE_INSTANCE',
    'assigned_cards': 'C__CATG__ASSIGNED_CARDS', 'person': 'C__CATS__PERSON',
    'logical_unit': 'C__CATG__LOGICAL_UNIT', 'organization': 'C__CATS__ORGANIZATION',
    'contract_assignment': 'C__CATG__CONTRACT_ASSIGNMENT',
    'chassis_devices': 'C__CATS__CHASSIS_DEVICES', 'stacking': 'C__CATG__STACKING',
    'share_access': 'C__CATG__SHARE_ACCESS',
    'nagios_refs_services': 'C__CATG__NAGIOS_REFS_SERVICES',
    'net_connector': 'C__CATG__NET_CONNECTOR',
    'cluster_adm_service': 'C__CATG__CLUSTER_ADM_SERVICE',
    'operating_system': 'C__CATG__OPERATING_SYSTEM', 'qinq_sp': 'C__CATG__QINQ_SP',
    'rm_controller': 'C__CATG__RM_CONTROLLER', 'file': 'C__CATG__FILE',
    'virtual_host': 'C__CATG__VRRP', 'vrrp': 'C__CATG__MANUAL',
    'manual': 'C__CATG__EMERGENCY_PLAN'
}
