from types import ModuleType
from typing import (
    Any,
    Callable,
    Generic,
    List,
    Optional,
    Type,
    TypedDict,
    TypeVar,
    Union,
)

from graia.saya.cube import Cube

from .context import channel_instance
from .schema import BaseSchema


class ChannelMeta(TypedDict):
    author: List[str]
    name: Optional[str]
    description: Optional[str]


M = TypeVar("M", bound=ChannelMeta)


class Channel(Generic[M]):
    module: str

    meta: M

    _export: Any = None
    _py_module: Optional[ModuleType] = None

    content: List[Cube]

    # TODO: _export reload for other modules

    def __init__(self, module: str) -> None:
        self.module = module
        self.meta: M = ChannelMeta(author=[], name=None, description=None)
        self.content = []

    @property
    def _name(self):
        return self.meta["name"]

    @_name.setter
    def _name(self, value: str):
        self.meta["name"] = value

    def name(self, name: str):
        self.meta["name"] = name
        return self

    @property
    def _author(self):
        return self.meta["author"]

    def author(self, author: str):
        self._author.append(author)
        return self

    @property
    def _description(self):
        return self.meta["description"]

    @_description.setter
    def _description(self, value: str):
        self.meta["description"] = value

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
