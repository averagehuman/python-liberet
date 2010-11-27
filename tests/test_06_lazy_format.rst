
::

    >>> import liberet
    >>> defaults = {
    ...     'APPID': 'TEST0',
    ...     'DATA_DIR': '/home/mylib/$APPID',
    ...     'NUMSERVERS': 4,
    ...     'osfs__FS_ARGS': ('$DATA_DIR/files', [0, '$NUMSERVERS']),
    ...     }
    >>> liberet.register(defaults, 'lazy', '')
    <liberet.ConfigHandle 'lazy'>
    >>> liberet.register(defaults, 'lazy', 'osfs')
    <liberet.ConfigHandle 'lazy::osfs'>
    >>> settings = liberet.get_config_handle('lazy')

``todict()``::

    >>> for item in sorted(settings.todict().iteritems()):
    ...     print('%s  ->  %s' % item)
    ...
    APPID  ->  TEST0
    DATA_DIR  ->  /home/mylib/TEST0
    NUMSERVERS  ->  4

    >>> for item in sorted(settings.osfs.todict().iteritems()):
    ...     print('%s  ->  %s' % item)
    ...
    APPID  ->  TEST0
    DATA_DIR  ->  /home/mylib/TEST0
    FS_ARGS  ->  ('/home/mylib/TEST0/files', [0, '4'])
    NUMSERVERS  ->  4

::

    >>> settings.APPID
    'TEST0'
    >>> settings.DATA_DIR
    '/home/mylib/TEST0'
    >>> settings.osfs.FS_ARGS
    ('/home/mylib/TEST0/files', [0, '4'])

