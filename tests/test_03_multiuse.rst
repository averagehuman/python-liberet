
Access other handles from a given handle
----------------------------------------

::

    >>> import change_default_settings_directory
    >>> import liberet

Clear any existing registries:

::

    >>> liberet.registries.clear()

Register handles::

    >>> defaults = {
    ...
    ...     'ALPHA': 'a',
    ...     'BETA': 'b',
    ...
    ...     'xxx__ALPHA': 'a (xxx)',
    ...     'xxx__BETA': 'b (xxx)',
    ...     'xxx__GAMMA': 'g (xxx)',
    ...
    ...     'yyy__ALPHA': 'a (yyy)',
    ...     'yyy__DELTA': 'd (yyy)',
    ...
    ... }
    ...
    >>> liberet.register(defaults, 'multiuse_settings', '')
    <liberet.ConfigHandle 'multiuse_settings'>
    >>> liberet.register(defaults, 'multiuse_settings', 'xxx')
    <liberet.ConfigHandle 'multiuse_settings::xxx'>
    >>> liberet.register(defaults, 'multiuse_settings', 'yyy')
    <liberet.ConfigHandle 'multiuse_settings::yyy'>

Choose any handle::

    >>> registry = liberet.registries.get('multiuse_settings')
    >>> handle = registry.get_handle('xxx')
    >>> handle
    <liberet.ConfigHandle 'multiuse_settings::xxx'>

Retrieve other handles using the prefix with which it was registered::

    >>> handle.yyy
    <liberet.ConfigHandle 'multiuse_settings::yyy'>

    >>> handle.ALPHA
    'a (xxx)'

Overrides - ``xxx__BETA`` is defined in ``conf.multiuse_settings.py``::

    >>> handle.BETA
    'overridden BETA value'

Values from other handles::

    >>> handle.yyy.ALPHA
    'a (yyy)'
    >>> handle.yyy.DELTA
    'd (yyy)'

Not defined, so fallthrough to default::

    >>> handle.yyy.BETA
    'b'

not defined and no default called GAMMA so exception::

    >>> handle.yyy.GAMMA
    Traceback (most recent call last):
        ...
    AttributeError: GAMMA

