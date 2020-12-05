import abc
from typing import List, Type

from graia.saya.entities.behaviour import Behaviour

class Schema(metaclass=abc.ABCMeta):
    require_behaviours: List[Type[Behaviour]]

    def __init__(self) -> None:
        pass