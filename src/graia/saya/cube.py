from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from .schema import BaseSchema

T = TypeVar("T", None, BaseSchema)


@dataclass(init=True)
class Cube(Generic[T]):
    content: Any
    metaclass: T
