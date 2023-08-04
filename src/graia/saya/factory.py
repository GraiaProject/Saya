import functools
from typing import Any, Callable, Dict, TypeVar

from typing_extensions import ParamSpec

from .channel import Channel
from .cube import Cube
from .schema import BaseSchema


def ensure_buffer(func: Callable) -> Dict[str, Any]:
    if not hasattr(func, "__schema_buffer__"):
        setattr(func, "__schema_buffer__", {})
    return getattr(func, "__schema_buffer__")


P = ParamSpec("P")
T_Callable = TypeVar("T_Callable", bound=Callable)
SchemaWrapper = Callable[[Callable, Dict[str, Any]], BaseSchema]
BufferModifier = Callable[[Dict[str, Any]], None]
Wrapper = Callable[[T_Callable], T_Callable]


def factory(func: Callable[P, SchemaWrapper]) -> Callable[P, Wrapper]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Wrapper:
        wrapper: SchemaWrapper = func(*args, **kwargs)

        def register(func: T_Callable) -> T_Callable:
            schema: BaseSchema = wrapper(func, ensure_buffer(func))
            Channel.current().content.append(Cube(func, schema))
            return func

        return register

    return wrapper


def buffer_modifier(func: Callable[P, BufferModifier]) -> Callable[P, Wrapper]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Wrapper:
        modifier: BufferModifier = func(*args, **kwargs)

        def modify(func: T_Callable) -> T_Callable:
            modifier(ensure_buffer(func))
            return func

        return modify

    return wrapper
