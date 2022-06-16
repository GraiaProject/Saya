import functools
import inspect
from types import ModuleType
from typing import (
    Any,
    Callable,
    Dict,
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


class ScopedContext:
    content: Dict[str, Any]

    def __init__(self, **kwargs) -> None:
        self.content = kwargs

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == "content":
            raise AttributeError("'ScopedContext' object attribute 'content' is not overwritable")

    def __getattr__(self, __name: str) -> Any:
        if __name == "content":
            return self.content
        if __name not in self.content:
            raise AttributeError(f"{__name} is not defined")
        return self.content[__name]


class Channel(Generic[M]):
    module: str

    meta: M

    _export: Any = None
    _py_module: Optional[ModuleType] = None

    content: List[Cube]

    scopes: Dict[Type, ScopedContext]

    # TODO: _export reload for other modules

    def __init__(self, module: str) -> None:
        self.module = module
        self.meta: M = ChannelMeta(author=[], name=None, description=None)
        self.content = []

    @property
    def _name(self):
        return self.meta["name"]

    @_name.setter
    def _name(self, value: Optional[str]):
        self.meta["name"] = value

    def name(self, name: str):
        self.meta["name"] = name
        return self

    @property
    def _author(self):
        return self.meta["author"]

    @_author.setter
    def _author(self, value: List[str]):
        self.meta["author"] = value

    def author(self, author: str):
        self._author.append(author)
        return self

    @property
    def _description(self):
        return self.meta["description"]

    @_description.setter
    def _description(self, value: Optional[str]):
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

    def scoped_context(self, isolate_class: Type[Any]):
        context = self.scopes.setdefault(
            isolate_class,
            ScopedContext(channel=self),
        )
        contents = {id(i.content): i for i in self.content}
        members = inspect.getmembers(isolate_class, lambda obj: callable(obj) and id(obj) in contents)
        # 用 id 的原因: 防止一些 unhashable 的对象给我塞进来.
        for _, obj in members:
            contents[id(obj)].content = functools.partial(obj, context)
        return isolate_class
