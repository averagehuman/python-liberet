
Override with '.ini'-style config
---------------------------------

::

    >>> import change_default_settings_directory
    >>> import liberet
    >>> liberet.registries.clear()

Setup::

    >>> sphinx_defaults = {'sphinx__rst_suffix': 'txt', 'sphinx__html_title': 'undefined'}
    >>> sphinx_settings = liberet.register(sphinx_defaults, 'settings.ini', prefix='sphinx', format='ini')
    >>> sphinx_settings
    <liberet.ConfigHandle 'settings.ini::sphinx'>
    >>> sphinx_settings.rst_suffix
    'rst'
    >>> sphinx_settings.html_title
    'undefined'

    >>> sphinx_settings.golem.nickname
    Traceback (most recent call last):
        ...
    AttributeError: golem

    >>> golem_defaults = {'golem__nickname': 'guest'}
    >>> golem_settings = liberet.register(golem_defaults, 'settings.ini', prefix='golem', format='ini')

    >>> sphinx_settings.golem.nickname
    'The Black Vegetable'


