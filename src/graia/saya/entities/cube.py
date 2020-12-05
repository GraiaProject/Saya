
import abc
from typing import Any, Generic, Hashable, List, Optional, Type, TypeVar
from graia.saya.entities.behaviour import Behaviour
from graia.saya.entities.schema import Schema

from graia.saya.entities.various import MountVarious, UnmountVarious

TV_CubeContent = TypeVar("TV_CubeContent")
TV_Schema = TypeVar("TV_Schema")

class Cube(Generic[TV_CubeContent, TV_Schema], metaclass=abc.ABCMeta):
    content: Optional[TV_CubeContent]
    schema: TV_Schema

    def __init__(self, schema: TV_Schema) -> None:
        self.schema = schema

    def onMount(self, various: MountVarious) -> None:
        pass
    
    def beforeUnmount(self, various: UnmountVarious) -> None:
        pass

    def setContent(self, target: TV_CubeContent) -> None:
        self.content = target
    
    def unsetContent(self) -> None:
        self.content = None
    
    @abc.abstractmethod
    def getUniqueKey(self) -> Hashable:
        pass

