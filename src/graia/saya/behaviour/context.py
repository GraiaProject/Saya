from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from graia.saya.cube import Cube

    from .entity import Behaviour


@dataclass(init=True)
class RequireContext:
    module: str
    behaviours: List["Behaviour"]
    _index: int = 0


@dataclass(init=True)
class AllocationContext:
    cube: "Cube"


@dataclass(init=True)
class RouteContext:
    module: str
