
from liberet import LazyRef

SETTING1 = 'global1'
SETTING2 = 'global2'

DELAYED_SETTING = LazyRef('conf.subdir.myapp.DELAYED_SETTING')

