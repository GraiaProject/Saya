"""Saya 相关的工具"""
from __future__ import annotations

import inspect
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Type,
    TypeVar,
    Union,
    overload,
)

from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.typing import T_Dispatcher
from graia.saya.factory import BufferModifier, SchemaWrapper, buffer_modifier, factory

from .schema import ListenerSchema

T_Callable = TypeVar("T_Callable", bound=Callable)
Wrapper = Callable[[T_Callable], T_Callable]

T = TypeVar("T")


def gen_subclass(cls: type[T]) -> Generator[type[T], Any, Any]:
    yield cls
    for sub in cls.__subclasses__():
        yield from gen_subclass(sub)


@buffer_modifier
def dispatch(*dispatcher: T_Dispatcher) -> BufferModifier:
    """附加参数解析器，最后必须接 `listen` 才能起效

    Args:
        *dispatcher (T_Dispatcher): 参数解析器

    Returns:
        Callable[[T_Callable], T_Callable]: 装饰器
    """

    return lambda buffer: buffer.setdefault("dispatchers", []).extend(dispatcher)


@overload
def decorate(*decorator: Decorator) -> Wrapper:
    """附加多个无头装饰器

    Args:
        *decorator (Decorator): 无头装饰器

    Returns:
        Callable[[T_Callable], T_Callable]: 装饰器
    """
    ...


@overload
def decorate(name: str, decorator: Decorator, /) -> Wrapper:
    """给指定参数名称附加装饰器

    Args:
        name (str): 参数名称
        decorator (Decorator): 装饰器

    Returns:
        Callable[[T_Callable], T_Callable]: 装饰器
    """
    ...


@overload
def decorate(mapping: Dict[str, Decorator], /) -> Wrapper:
    """给指定参数名称附加装饰器

    Args:
        mapping (Dict[str, Decorator]): 参数名称与装饰器的映射

    Returns:
        Callable[[T_Callable], T_Callable]: 装饰器
    """
    ...


@buffer_modifier
def decorate(*args) -> BufferModifier:
    """给指定参数名称附加装饰器

    Args:
        name (str | Dict[str, Decorator]): 参数名称或与装饰器的映射
        decorator (Decorator): 装饰器

    Returns:
        Callable[[T_Callable], T_Callable]: 装饰器
    """
    arg: Union[Dict[str, Decorator], List[Decorator]]
    if isinstance(args[0], str):
        name: str = args[0]
        decorator: Decorator = args[1]
        arg = {name: decorator}
    elif isinstance(args[0], dict):
        arg = args[0]
    else:
        arg = list(args)

    def wrapper(buffer: Dict[str, Any]) -> None:
        if isinstance(arg, list):
            buffer.setdefault("decorators", []).extend(arg)
        elif isinstance(arg, dict):
            buffer.setdefault("decorator_map", {}).update(arg)

    return wrapper


@buffer_modifier
def priority(level: int, *events: Type[Dispatchable]) -> BufferModifier:
    """设置事件优先级

    Args:
        level (int): 事件优先级
        *events (Type[Dispatchable]): 提供时则会设置这些事件的优先级, 否则设置全局优先级

    Returns:
        Callable[[T_Callable], T_Callable]: 装饰器
    """

    def wrapper(buffer: Dict[str, Any]) -> None:
        if events:
            buffer.setdefault("extra_priorities", {}).update((e, level) for e in events)
        else:
            buffer["priority"] = level

    return wrapper


@factory
def listen(*event: Union[Type[Dispatchable], str]) -> SchemaWrapper:
    """在当前 Saya Channel 中监听指定事件

    Args:
        *event (Union[Type[Dispatchable], str]): 事件类型或事件名称

    Returns:
        Callable[[T_Callable], T_Callable]: 装饰器
    """
    EVENTS: Dict[str, Type[Dispatchable]] = {e.__name__: e for e in gen_subclass(Dispatchable)}
    events: List[Type[Dispatchable]] = [e if isinstance(e, type) else EVENTS[e] for e in event]

    def wrapper(func: Callable, buffer: Dict[str, Any]) -> ListenerSchema:
        decorator_map: Dict[str, Decorator] = buffer.pop("decorator_map", {})
        buffer["inline_dispatchers"] = buffer.pop("dispatchers", [])
        if decorator_map:
            sig = inspect.signature(func)
            for param in sig.parameters.values():
                if decorator := decorator_map.get(param.name):
                    setattr(param, "_default", decorator)
            func.__signature__ = sig
        return ListenerSchema(listening_events=events, **buffer)

    return wrapper
