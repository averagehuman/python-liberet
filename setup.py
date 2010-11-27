# -*- coding: utf-8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

import re
version_rx = r"^__version__ = '(.*)'$"
version_pattern = re.compile(version_rx)


fd = open('liberet.py')
try:
    for line in fd:
        m = version_pattern.match(line)
        if m:
            break
    else:
        raise Exception("couldn't find __version__")
finally:
    fd.close()

__version__ = m.group(1)

print "running setup for liberet version %s" % __version__

requires = ['importlib']


setup(
        name="liberet",
        version=__version__,
        description="Library configuration mechanism derived from google.appengine.api.lib_config",
        author="Walter Wefft",
        author_email = "walter@wefft.com",
        classifiers=["Development Status :: 4 - Beta",
                    "Intended Audience :: Developers",
                    "Programming Language :: Python",
                    "Topic :: Software Development :: Libraries",
                    "Topic :: Software Development :: Libraries :: Python Modules",
                    ],
        url="http://wefft.codebasehq.com/wefft/lib/liberet.hg",
        license="Apache",
        download_url="http://pypi.python.org/packages/source/l/liberet/liberet-%s.tar.gz" % __version__,
        py_modules=['liberet'],
        install_requires=requires,
)
    
