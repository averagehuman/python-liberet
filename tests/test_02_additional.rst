
Defaults can be specified in a module or class
----------------------------------------------

::

    >>> import change_default_settings_directory
    >>> import liberet
    >>> liberet.registries.clear()

Module level defaults (can be given as a string or an object)::

    >>> defaults = 'conf.subdir.global_settings'
    >>> settings = liberet.register(defaults, 'mylib')
    >>> settings
    <liberet.ConfigHandle 'mylib'>
    >>> settings.SETTING1
    'global1'

Class object defaults (default_object is defined in `conf.subdir.__init__.py`)::

    >>> defaults = 'conf.subdir.default_object'
    >>> settings = liberet.register(defaults, 'mylib')
    >>> settings
    <liberet.ConfigHandle 'mylib'>
    >>> settings.SETTING1
    'this is a class level attribute'


Delayed Settings
----------------

::

    >>> liberet.registries.clear()

    >>> defaults = 'conf.subdir.global_settings'
    >>> settings = liberet.register(defaults, 'mylib')
    >>> settings
    <liberet.ConfigHandle 'mylib'>
    >>> settings.DELAYED_SETTING
    'delayed value'

Required Settings
-----------------

::

    >>> liberet.registries.clear()

    >>> defaults = 'conf.subdir.other_settings'
    >>> settings = liberet.register(defaults, 'mylib')
    >>> settings
    <liberet.ConfigHandle 'mylib'>
    >>> settings.REQUIRED_SETTING
    Traceback (most recent call last):
        ...
    LiberetRequiredSetting: REQUIRED_SETTING not found in module conf.mylib


Unspecified module name
-----------------------

If you don't specify the settings module it defaults to the value of ``LIBERET_SETTINGS_MODULE``,
which is 'settings' by default, but here is 'conf'::

    >>> liberet.registries.clear()

    >>> defaults = {'X': liberet.Required}
    >>> settings = liberet.register(defaults)
    >>> settings
    <liberet.ConfigHandle 'conf'>
    >>> settings.X
    Traceback (most recent call last):
        ...
    LiberetRequiredSetting: X not found in module conf


LazyRef
-------

::

    >>> dirname = liberet.LazyRef('os.path.dirname')
    >>> dirname('a/b/c')
    'a/b'
    >>> match = liberet.LazyRef('re.match')
    >>> m = match(r'#(.*)#', '#onetwo#')
    >>> m.group(1)
    'onetwo'


