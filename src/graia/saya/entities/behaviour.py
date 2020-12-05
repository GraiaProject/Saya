import abc
from typing import Dict, List, Optional


class Behaviour(metaclass=abc.ABCMeta):
    manage_cubes: List["Cube"]
    manage_isolates: Dict["Isolate", List["Cube"]]

    def __init__(self) -> None:
        self.manage_cubes = []
        self.manage_isolates = {}

    @abc.abstractmethod
    def mountCube(self, cube: "Cube", using_isolates: Optional["Isolate"] = None):
        pass

    @abc.abstractmethod
    def unmountCube(self, cube: "Cube"):
        pass

from .isolate import Isolate
from .cube import Cube