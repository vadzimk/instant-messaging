import inspect
import sys

from .base_schema import *
from .user_schema import *
from .contact_schema import *
from .message_schema import *


__all__ = [
    name for name, obj in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(obj) and issubclass(obj, BaseModel)
]
