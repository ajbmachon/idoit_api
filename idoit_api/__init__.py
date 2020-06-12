import os
import os.path as osp
from idoit_api.const import LOG_PATH

if not osp.exists(LOG_PATH):
    os.makedirs(LOG_PATH)
