
# change the default settings directory ('settings') to 'conf':

import os
import liberet

settingsdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')

os.environ[liberet.LIBERET_SETTINGS_DIRECTORY] = settingsdir



