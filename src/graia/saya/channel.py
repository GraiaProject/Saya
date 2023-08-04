from __future__ import annotations

import functools
import inspect
from types import ModuleType
from typing import (
    TYPE_CHECKING,
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
    cast,
)

try:
    from importlib_metadata import distribution
except ImportError:
    from importlib.metadata import distribution

from graia.saya.cube import Cube

if TYPE_CHECKING:
    from typing_extensions import NotRequired

from .context import channel_instance
from .schema import BaseSchema


class ChannelMeta(TypedDict):
    author: List[str]
    name: NotRequired[str]
    version: NotRequired[str]
    license: NotRequired[str]
    urls: NotRequired[Dict[str, str]]
    description: NotRequired[str]
    icon: NotRequired[str]
    classifier: List[str]
    dependencies: List[str]

    standards: List[str]
    frameworks: List[str]
    config_endpoints: List[str]
    component_endpoints: List[str]


def _default_channel_meta() -> ChannelMeta:
    return ChannelMeta(
        author=[],
        classifier=[],
        dependencies=[],
        standards=[],
        frameworks=[],
        config_endpoints=[],
        component_endpoints=[],
    )


def get_channel_meta(module: str) -> ChannelMeta:
    dist = distribution(module)
    meta = cast(Dict[str, Any], _default_channel_meta())
    meta |= dist.metadata.json
    if meta["author"]:  # "author" in dist.metadata.json and dist.metadata.json["author"]
        meta["author"] = meta["author"].split(",")
    elif "author_email" in meta:
        meta["author"] = meta["author_email"].split(",")
    meta["urls"] = dict(i.split(", ") for i in meta.get("project_url", ()))
    meta["dependencies"] = dist.requires or []
    return cast(ChannelMeta, meta)


M = TypeVar("M", bound=ChannelMeta)


class ScopedContext:
    content: Dict[str, Any]

    def __init__(self, **kwargs) -> None:
        self.content = kwargs

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == "content":
            raise AttributeError("'ScopedContext' object attribute 'content' is not overwritable")
        self.content[__name] = __value

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
        self.meta = cast(M, _default_channel_meta())
        self.content = []

    @staticmethod
    def current() -> "Channel":
        """获取当前的 Channel 对象

        Returns:
            Channel: 当前的 Channel 对象
        """
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
