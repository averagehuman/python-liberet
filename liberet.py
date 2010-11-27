#
# Copyright 2010 Walter Wefft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This is derivative work based on the `lib_config` module in the Google
# AppEngine Python SDK available here
#
#         http://code.google.com/appengine/downloads.html
#
# The original work has the following notice
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import os
import sys
import inspect
import types
import string

try:
    from importlib import import_module
except ImportError:
    try:
        from django.utils.importlib import import_module
    except ImportError:
        try:
            from djangosans.importlib import import_module
        except ImportError:
            raise ImportError('importlib')

__all__ = [
            'register',
            'registries',
            'is_registered',
            'get_config_handle',
            'import_name',
            'LazyRef',
            'Required',
            'LibConfigRegistry',
            'ConfigHandle',
            'LiberetException',
            'LiberetRequiredSetting',
            'LIBERET_SETTINGS_DIRECTORY ',
            ]

__version__ = '0.8.9'


#LIBERET_SETTINGS_DIRECTORY = os.path.abspath(os.environ.get('LIBERET_SETTINGS_DIRECTORY', 'settings'))
LIBERET_SETTINGS_DIRECTORY = 'LIBERET_SETTINGS_DIRECTORY'
Template = string.Template

class LiberetException(Exception):
    message = None
    def __str__(self):
        return self.message or self.__doc__

class MissingEnvironmentVariable(LiberetException):
    def __init__(self, var):
        self.message = var

class LiberetRequiredSetting(LiberetException):
    """Setting not found."""

    def __init__(self, settingkey, modname):
        #if settingkey.startswith('__'):
        #    settingkey = settingkey[2:]
        #if settings_module != LIBERET_SETTINGS_DIRECTORY:
        module_dir = get_settings_module()
        if modname != module_dir:
            modname = '.'.join((module_dir, modname))
        self.message = "%s not found in module %s" % (settingkey, modname)

def get_settings_path():
    try:
        fullpath = os.path.abspath(os.environ[LIBERET_SETTINGS_DIRECTORY])
    except KeyError:
        raise MissingEnvironmentVariable(LIBERET_SETTINGS_DIRECTORY)
    if not os.path.exists(fullpath):
        raise EnvironmentError("settings path does not exist: %s" % fullpath)
    parent, modname = os.path.dirname(fullpath), os.path.basename(fullpath)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    return parent, modname

def get_project_path():
    return get_settings_path()[0]

def get_settings_module():
    return get_settings_path()[1]

def import_name(name, package=None):
    try:
        return import_module(name, package)
    except ImportError:
        try:
            m, k = name.rsplit('.', 1)
        except ValueError:
            raise ImportError(name)
        m = import_module(m)
        return getattr(m, k)

def import_py(modname):
    projectdir, settings_module = get_settings_path()
    if not modname.startswith(settings_module):
        modname = '%s.%s' % (settings_module, modname)
    m = import_module(modname)
    return m

def import_ini(modname, parser=None):
    import ConfigParser
    if parser is None:
        parser = ConfigParser.SafeConfigParser
    projectdir, settings_module = get_settings_path()
    inifile = os.path.join(projectdir, settings_module, modname)
    config = parser()
    readok = config.read(inifile)
    if not readok:
        raise ImportError("No module named %s" % modname)
    d = {}
    for sectname in config.sections():
        if sectname == ConfigParser.DEFAULTSECT:
            prefix = ''
        else:
            prefix = sectname + '__'
        for option in config.options(sectname):
            d[prefix+option] = config.get(sectname, option)
    m = get_sys_module(modname)
    if m:
        m.__dict__.update(d)
    else:
        # need something with a __dict__:
        set_sys_module(modname, type('ProxyModule', (object,), d))

def import_dubbel(modname):
    from dubbel import DubbelParser
    import_ini(modname, parser=DubbelParser)


importers = {
        'py': import_py,
        'dubbel': import_dubbel,
        'ini': import_ini,
        }

class LazyRef(object):

    def __init__(self, objname):
        self._objname = objname
        self._obj = None

    def get_object(self):
        if self._obj is None:
            self._obj = import_name(self._objname)
        return self._obj

    def __call__(self, *args, **kw):
        return self.get_object()(*args, **kw)

class RequiredType(type):
    pass

class Required(object):
    __metaclass__ = RequiredType

def normalize_defaults(defaults):
    if defaults is None:
        return {}
    if isinstance(defaults, basestring):
        defaults = import_name(defaults)
    if hasattr(defaults, '__getitem__'):
        return defaults
    if hasattr(defaults, '__dict__'):
        return defaults.__dict__
    raise TypeError("Defaults must be a mapping, object or module type: %s" % defaults)

def is_registered(modname, prefix=''):
    reg = registries.get(modname)
    if reg:
        return prefix in reg._registrations
    return False

def get_sys_module(modname):
    module_dir = get_settings_module()
    if modname != module_dir:
        modname = '.'.join((module_dir, modname))
    return sys.modules.get(modname, None)

def set_sys_module(modname, module_obj):
    module_dir = get_settings_module()
    if modname != module_dir:
        modname = '.'.join((module_dir, modname))
    sys.modules[modname] = module_obj

def remove_sys_module(modname):
    module_dir = get_settings_module()
    if modname != module_dir:
        modname = '.'.join((module_dir, modname))
    if modname in sys.modules:
        del sys.modules[modname]

class RegistrySet(object):

    def __init__(self):
        self._registries = {}

    def add(self, modname, registry):
        self._registries[modname] = registry

    def remove(self, modname):
        del self._registries[modname]

    def clear(self):
        for modname, registry in self._registries.iteritems():
            for handle in registry._registrations.itervalues():
                handle.clear()
            remove_sys_module(modname)
        del self._registries
        self._registries = {}

    def __contains__(self, modname):
        return modname in self._registries

    def get(self, modname):
        return self._registries.get(modname)

    def is_initialized(self, modname):
        try:
            return self._registries[modname]._module is not None
        except KeyError:
            return False

registries = RegistrySet()

def register(defaults, settings_module_name=None, prefix='', format='py', cascade=True):
    defaults = normalize_defaults(defaults)
    settings_module_name = settings_module_name or get_settings_module()
    prefix = prefix#or defaults.get(PREFIXVAR, '')
    if not isinstance(settings_module_name, basestring):
        raise TypeError("settings_module_name must be a string")
    registry = registries.get(settings_module_name)
    if registry is None:
        registry = LibConfigRegistry(settings_module_name, format)
    else:
        assert format == registry.format
    handle = registry.register(prefix, defaults, cascade=cascade)
    return handle

def get_config_handle(modname, prefix=None):
    prefix = prefix or ''
    reg = registries.get(modname)
    if reg:
        return reg.get_handle(prefix)

class LibConfigRegistry(object):
    """A registry for library configuration values."""

    def __init__(self, modname, format="py"):
        """Constructor.

        Args:
            modname: The module name to be imported.

        Note: the actual import of this module is deferred until the first
        time a configuration value is requested through attribute access
        on a ConfigHandle instance.
        """
        global registries
        self._modname = modname
        self._registrations = {}
        self._module = None
        self.format = format
        self._importer = importers[format]
        self._required = set()
        if registries is None:
            registries = RegistrySet()
        registries.add(modname, self)

    def register(self, prefix, mapping, cascade=True):
        """Register a set of configuration names.

        Args:
            prefix: A shared prefix for the configuration names being registered.
                    If the prefix doesn't end in '_', that character is appended.
            mapping: A dict mapping suffix strings to default values.

        Returns:
            A ConfigHandle instance.

        It's okay to re-register the same prefix: the mappings are merged,
        and for duplicate suffixes the most recent registration wins.
        """
        handle = self._registrations.get(prefix)
        if handle is None:
            handle = ConfigHandle(prefix, self, cascade=cascade)
            self._registrations[prefix] = handle
        handle._update_defaults(mapping)
        return handle

    def get_handle(self, prefix):
        return self._registrations.get(prefix)

    def is_registered(self, prefix):
        return self.get_handle(prefix) is not None

    def initialize(self):
        """Attempt to import the config module, if not already imported.

        This function always sets self._module to a value unequal
        to None: either the imported module (if imported successfully), or
        a dummy object() instance (if an ImportError was raised).    Other
        exceptions are *not* caught.

        When a dummy instance is used, it is also put in sys.modules.
        This allows us to detect when sys.modules was changed (as
        dev_appserver.py does when it notices source code changes) and
        re-try the __import__ in that case, while skipping it (for speed)
        if nothing has changed.

        """
        modname = self._modname
        if self._module is not None and self._module is get_sys_module(modname):
            return
        try:
            self._importer(modname)
        except ImportError:
            self._module = object()
            set_sys_module(modname, self._module)
        else:
            self._module = get_sys_module(modname)
            for key in self._required:
                if key not in self._module.__dict__:
                    raise LiberetRequiredSetting(key, modname)

    def _pairs(self, prefix):
        """Generate (key, value) pairs from the config module matching prefix.

        Args:
            prefix: A prefix string

        Yields:
            (key, value) pairs where key is the configuration name with
            prefix removed, and value is the corresponding value.
        """
        assert not prefix.endswith('__')
        if prefix:
            prefix += '__'
        mapping = getattr(self._module, '__dict__', None)
        if not mapping:
            return
        nskip = len(prefix)
        for key, value in mapping.iteritems():
            if prefix:
                if key.startswith(prefix):
                    yield key[nskip:], value
            elif '__' not in key:
                yield key, value

    def _dump(self):
        """Print info about all registrations to stdout."""
        self.initialize()
        if not hasattr(self._module, '__dict__'):
            print 'Module %s.py does not exist.' % self._modname
        elif not self._registrations:
            print 'No registrations for %s.py.' % self._modname
        else:
            print 'Registrations in %s.py:' % self._modname
            print '-'*40
            for prefix in sorted(self._registrations):
                self._registrations[prefix]._dump()

class ConfigHandle(object):
    """A set of configuration for a single library module or package.

    Public attributes of instances of this class are configuration
    values.    Attributes are dynamically computed (in __getattr__()) and
    cached as regular instance attributes.
    """

    _initialized = False

    def __init__(self, prefix, registry, cascade=True):
        """Constructor.

        Args:
            prefix: A shared prefix for the configuration names being registered.
            registry: A LibConfigRegistry instance.
            strict: If True, config values  will be looked up only on this ConfigHandle
                    instance, otherwise all registered handles will be checked.
        """
        assert not prefix.endswith('__')
        self._prefix = prefix
        self._defaults = {}
        self._overrides = {}
        self._registry = registry
        self._cascade = cascade

    @property
    def registry(self):
        return self._registry

    def _update_defaults(self, mapping):
        """Update the default mappings.

        Args:
            mapping: A dict mapping suffix strings to default values.
        """
        mapping = normalize_defaults(mapping)
        required = self._registry._required
        M = types.ModuleType
        for key, value in mapping.iteritems():
            if key.startswith('_') or key in __all__ or isinstance(value, M):
                continue
            # if we expect a prefix then it must be the right prefix
            # if we don't expect a prefix then ignore anything that has a prefix
            parts = key.split('__', 1)
            if self._prefix:
                if len(parts) == 2 and parts[0] == self._prefix:
                    key = parts[1]
                else:
                    continue
            else:
                if len(parts) != 1:
                    continue
            self._defaults[key] = value
            if value is Required:# and key != 'Required':
                required.add(key)
        if self._initialized:
            self._update_configs()

    def _update_configs(self):
        """Update the configuration values.

        This clears the cached values, initializes the registry, and loads
        the configuration values from the config module.
        """
        if self._initialized:
            self.clear()
        self._registry.initialize()
        for key, value in self._registry._pairs(self._prefix):
            if key not in self._defaults:
                continue
            else:
                self._overrides[key] = value
        self._initialized = True

    def clear(self):
        """
        Clear the the values that have been cached on the instance.
        (Use del if you also want to remove from defaults)
        """
        for key in self._defaults:
            try:
                del self.__dict__[key]
            except KeyError:
                pass

    def _dump(self):
        """Print info about this set of registrations to stdout."""
        print 'Prefix %s:' % self._prefix
        if self._overrides:
            print '    Overrides:'
            for key in sorted(self._overrides):
                print '        %s = %r' % (key, self._overrides[key])
        else:
            print '    No overrides'
        if self._defaults:
            print '    Defaults:'
            for key in sorted(self._defaults):
                print '        %s = %r' % (key, self._defaults[key])
        else:
            print '    No defaults'
        print '-'*40

    def _getattr(self, key):
        """Dynamic attribute access.

        Args:
            key: The attribute name.

        Returns:
            A configuration values.

        Raises:
            AttributeError if the key is not a registered key.

        The first time an attribute is referenced, this method is invoked.
        The value returned taken either from the config module or from the
        registered default.
        """
        if not self._initialized:
            self._update_configs()
        if key in self._overrides:
            value = self._overrides[key]
        elif key in self._defaults:
            value = self._defaults[key]
            if isinstance(value, RequiredType):
                if self._prefix:
                    key = '%s__%s' % (self._prefix, key)
                raise LiberetRequiredSetting(key, self._registry._modname)
        else:
            raise AttributeError(key)
        if isinstance(value, LazyRef):
            return value.get_object()
        return value
        

    def __getattr__(self, key):
        value = undefined = object() # can't use None, as this may be a valid setting value
        # If suffix is a registered prefix :-) return the associated config handle.
        handle = self._registry.get_handle(key)
        if handle is not None:
            value = handle
        else:
            # otherwise look for a setting with this suffix
            try:
                value = self._getattr(key)
            except AttributeError:
                if self._prefix and self._cascade:
                    # look for default
                    registry_defaults = self._registry.get_handle('')
                    if registry_defaults:
                        try:
                            value = registry_defaults._getattr(key)
                        except AttributeError:
                            pass
        if value is undefined:
            raise AttributeError(key)
        else:
            value = self.interpolate(value)
            setattr(self, key, value) # cache the value in instance
            return value

    def todict(self):
        d = None
        if self._prefix:
            registry_defaults = self._registry.get_handle('')
            if registry_defaults:
                d = registry_defaults.todict()
        d = d or {}
        d.update(self._defaults)
        d.update(self._overrides)
        for k in d:
            d[k] = self.interpolate(d[k], d)
        return d

    def interpolate(self, value, context=None):
        context = context or self.todict()
        if hasattr(value, 'iterkeys') and not isinstance(value, self.__class__):
            for k in value.iterkeys():
                value[k] = self.interpolate(value[k], context)
        elif hasattr(value, '__iter__'):
            value = type(value)(self.interpolate(item, context) for item in value)
        else:
            try:
                value = Template(value).safe_substitute(context)
            except TypeError:
                pass
        return value

    def __hasattr__(self, name):
        try:
            val = self.__getattr__(name)
        except AttributeError:
            return False
        return True

    def __contains__(self, name):
        return hasattr(self, name)

    def __delattr__(self, name):
        """clear from instance AND defaults, so that name is no longer accessible"""
        try:
            del self.__dict__[name]
        except KeyError:
            pass
        del self._defaults[name]
        if self._prefix:
            name = '%s__%s' % (self._prefix, name)
        try:
            m = get_sys_module(self._registry._modname)
            del m.__dict__[name]
        except (KeyError, AttributeError):
            pass

    def __repr__(self):
        if self._prefix:
            return "<liberet.ConfigHandle '%s::%s'>" % (self._registry._modname, self._prefix)
        else:
            return "<liberet.ConfigHandle '%s'>" % self._registry._modname

    # dict methods
    def get(self, key, default=None):
        try:
            return self.__getattr__(key)
        except AttributeError:
            return default

    def __getitem__(self, key):
        return self.__getattr__(key)

    def iterkeys(self):
        return self._defaults.iterkeys()

    def itervalues(self):
        for k in self._defaults.iterkeys():
            yield self.__getattr__(k)

    def iteritems(self):
        for k in self._defaults.iterkeys():
            yield k, self.__getattr__(k)


