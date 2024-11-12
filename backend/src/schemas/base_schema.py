from dataclasses import field
from typing import Tuple, Any, List

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    model_config = {
        "from_attributes": True,  # model_validate will be able to take a dict or orm.model
    }


class ValidationError(BaseModel):
    type: str  # related type
    loc: Tuple[str]  # location of error
    msg: str
    input: Any  # actual input
    url: str  # more info about this error


class SioResponseSchema(BaseModel):
    success: bool = True
    data: Any
    errors: List[ValidationError | str] = field(default_factory=list)

    model_config = {
        'arbitrary_types_allowed': True
    }
