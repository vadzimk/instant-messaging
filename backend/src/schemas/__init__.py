import inspect
import sys

from .base_schema import *
from .user_schema import *
from .contact_schema import *
from .message_schema import *
from .telegram_schema import *
from .health_schema import *
# if you add more modules remember to add an import here!!!!


__all__ = [
    name for name, obj in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(obj) and issubclass(obj, BaseModel)
]

# Automatically export all Schema classes, no need to remember to add import in the __init__.py
# This works when i test it like this: python -m src.schemas
# but not working in the codebase
# import inspect
# import glob
# from importlib import import_module
# from os.path import dirname, basename, isfile, join
#
# modules = glob.glob(join(dirname(__file__), '*.py'))  # list of paths in dir
#
# module_names = [
#     basename(f)[:-3]
#     for f in modules
#     if isfile(f) and not f.endswith('__init__.py')
# ]
#
# # capture BaseModel
# BaseModel = None
# for module_name in module_names:
#     module = import_module(f'{__name__}.{module_name}')
#
#     for name, obj in inspect.getmembers(module):
#         if inspect.isclass(obj) and name == 'BaseModel':
#             BaseModel = obj
#             break
#     if BaseModel:
#         break
#
# # find and export all subclasses of BaseModel across modules
# __all__ = []
# for module_name in module_names:
#     module = import_module(f'{__name__}.{module_name}')
#     # find BaseModel subclasses
#     for name, obj in inspect.getmembers(module):
#         if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
#             __all__.append(name)
#
# print(__all__)