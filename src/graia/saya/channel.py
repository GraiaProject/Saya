from typing import Any, List, Optional, Tuple, Type, Union, Callable
from types import ModuleType

from graia.saya.cube import Cube

from .schema import BaseSchema
from .context import channel_instance

class Channel:
    module: str
    _name: Optional[str] = None
    _author: List[str]
    _description: Optional[str] = None

    _export: Any = None
    _py_module: Optional[ModuleType] = None

    content: List[Cube]

    # TODO: _export reload for other modules

    def __init__(self, module: str) -> None:
        self.module = module
        self._author = []
        self.content = []

    def name(self, name: str):
        self._name = name
        return self

    def author(self, author: str):
        self._author.append(author)
        return self

    def description(self, description: str):
        self._description = description
        return self

    @staticmethod
    def current() -> "Channel":
        return channel_instance.get()

    def export(self, target):
        self._export = target
        return target

    def use(self, schema: BaseSchema):
        def use_wrapper(target: Union[Type, Callable, Any]):
            self.content.append(Cube(target, schema))
            return target
        return use_wrapper

    def cancel(self, target: Union[Type, Callable, Any]):
        self.content = [i for i in self.content if i.content is not target]
