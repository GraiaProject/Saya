from typing import Any, Generic, TypeVar
from .schema import BaseSchema
from dataclasses import dataclass

T = TypeVar("T", None, BaseSchema)

@dataclass(init=True)
class Cube(Generic[T]):
    content: Any
    metaclass: T