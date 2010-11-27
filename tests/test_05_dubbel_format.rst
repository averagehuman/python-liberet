
Using dubbel for settings overrides
-----------------------------------

``dubbel`` is a ConfigParser/YAML hybrid config format::

    >>> import change_default_settings_directory
    >>> import liberet
    >>> liberet.registries.clear()

    >>> fp = open('conf/dubbel_settings.yaml')
    >>> print(fp.read().strip())
    [sphinx]
    <BLANKLINE>
        rst_suffix: rst
        extensions:
            - doctest
            - autodoc
    <BLANKLINE>
    [jekyll]
    <BLANKLINE>
        copyright: John J. Jaffa
    >>> fp.close()

Register setting::

    >>> sphinx_defaults = {'sphinx__rst_suffix': 'txt', 'sphinx__extensions': ['doctest', 'jsmath']}
    >>> sphinx_settings = liberet.register(sphinx_defaults, 'dubbel_settings.yaml', 'sphinx', format='dubbel')
    >>> sphinx_settings
    <liberet.ConfigHandle 'dubbel_settings.yaml::sphinx'>
    >>> sphinx_settings.rst_suffix
    'rst'

Register more settings::

    >>> jekyll_defaults = {'jekyll__copyright': 'Not Defined', 'jekyll__css_style': 'default'}
    >>> jekyll_settings = liberet.register(jekyll_defaults, 'dubbel_settings.yaml', 'jekyll', format='dubbel')
    >>> jekyll_settings
    <liberet.ConfigHandle 'dubbel_settings.yaml::jekyll'>
    >>> jekyll_settings.copyright
    'John J. Jaffa'
    >>> jekyll_settings.css_style
    'default'

multiuse::

    >>> jekyll_settings.sphinx.rst_suffix
    'rst'
    >>> sphinx_settings.jekyll.copyright
    'John J. Jaffa'

mmm...::

    >>> sphinx_settings.sphinx.rst_suffix
    'rst'
    >>> sphinx_settings.sphinx.sphinx.rst_suffix
    'rst'

