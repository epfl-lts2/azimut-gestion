import pkgutil
import inspect

wizs = {}

from _wizard import _Wizard

for importer, modname, ispkg in pkgutil.iter_modules(__path__):
    if not ispkg:
        module = __import__(modname, locals(), [], -1)
        for name, cls in inspect.getmembers(module):
            if inspect.isclass(cls) and issubclass(cls, _Wizard) and cls.__name__[0] != '_':
                wizs.update({cls.__name__: cls})
