from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

DataType = TypeVar("DataType")

class IResponseBase(GenericModel, Generic[DataType]):
    status: bool = True
    response: Optional[DataType] = None