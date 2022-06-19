from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar

from .schema import BaseSchema

T = TypeVar("T", bound=Optional[BaseSchema])


@dataclass(init=True)
class Cube(Generic[T]):
    content: Any
    metaclass: T
