from typing import Callable, Dict, Any, TypeVar
from .cube import Cube
from .schema import BaseSchema
from .channel import Channel
from typing_extensions import ParamSpec
import functools


def ensure_buffer(func: Callable) -> Dict[str, Any]:
    if not hasattr(func, "__schema_buffer__"):
        setattr(func, "__schema_buffer__", {})
    return getattr(func, "__schema_buffer__")


P = ParamSpec("P")
T_Callable = TypeVar("T_Callable", bound=Callable)
SchemaWrapper = Callable[[Callable], BaseSchema]
Wrapper = Callable[[T_Callable], T_Callable]


def factory(func: Callable[P, SchemaWrapper]) -> Callable[P, Wrapper]:
    @functools.wraps(func)
    def surface(*args: P.args, **kwargs: P.kwargs) -> Wrapper:
        wrapper: SchemaWrapper = func(*args, **kwargs)

        def register(func: T_Callable) -> T_Callable:
            schema: BaseSchema = wrapper(func)
            Channel.current().content.append(Cube(func, schema))
            return func

        return register

    return surface
