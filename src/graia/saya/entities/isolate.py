import abc
from typing import Generic, TypeVar

TV_IsolateLayer = TypeVar("TV_IsolateLayer")

class Isolate(Generic[TV_IsolateLayer], metaclass=abc.ABCMeta):
    """应该是 '永存' 的, 或者随着 layer 消失.
    只是标识, 类似 group 上的 tag
    在针对 Isolate 进行操作时, 应该给出所有能给出的符合条件的 Saya 所辖对象和 Isolate 本身.
    """

    layer: TV_IsolateLayer

    def __init__(self) -> None:
        pass