
liberet
=======

Basic Usage
-----------

Import liberet::

    >>> import liberet

Ensure no existing registries::

    >>> liberet.registries.clear()

Register settings values. Here defaults are a dictionary but they can also be defined
in a module or class::

    >>> defaults = {'SETTING1': 'undefined', 'SETTING2': 'undefined'}

My library is called ``mylib`` so I expect users to supply overrides to the defaults
in a module called ``mylib.py`` within the settings directory::

    >>> settings = liberet.register(defaults, 'mylib')
    >>> settings
    <liberet.ConfigHandle 'mylib'>


SETTING1 hasn't been overridden in the user-supplied (``mylib.py``) and so has the
default value::

    >>> settings.SETTING1
    'undefined'

SETTING2 however takes its value from ``mylib.py``::

    >>> settings.SETTING2
    'overridden'
    

Imports are lazy
----------------

Settings are not imported until first access of an option::

    >>> appsettings = 'user_settings_2'
    >>> appsettings_module = 'conf.user_settings_2'

Module is not imported::

    >>> import sys
    >>> appsettings_module in sys.modules
    False

and not initialised as far as ``liberet`` is concerned::

    >>> liberet.registries.is_initialized(appsettings)
    False

Register the settings::

    >>> defaults = {'SETTING1': 'undefined', 'SETTING2': 'undefined'}
    >>> settings2 = liberet.register(defaults, appsettings)

still not imported::

    >>> appsettings_module in sys.modules
    False
    >>> liberet.registries.is_initialized(appsettings)
    False

now retrieve a settings value::

    >>> settings2.SETTING1
    'app2 user settings'

which triggers import and initialisation::

    >>> appsettings_module in sys.modules
    True
    >>> liberet.registries.is_initialized(appsettings)
    True

