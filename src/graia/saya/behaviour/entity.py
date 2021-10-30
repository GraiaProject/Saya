from abc import ABCMeta, abstractmethod
from typing import Any

from graia.saya.cube import Cube


class Behaviour(metaclass=ABCMeta):
    @abstractmethod
    def allocate(self, cube: Cube[Any]) -> Any:
        pass

    @abstractmethod
    def uninstall(self, cube: Cube[Any]) -> Any:
        pass
