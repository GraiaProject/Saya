import itertools
from typing import TYPE_CHECKING, Any, Generator, List

from graia.broadcast.exceptions import RequirementCrashed

from graia.saya.cube import Cube

from .context import AllocationContext, RequireContext
from .entity import Behaviour

if TYPE_CHECKING:
    from graia.saya import Saya

# TODO: Lifecycle for Behaviour


class BehaviourInterface:
    saya: "Saya"

    require_contents: List[RequireContext]

    def __init__(self, saya_instance: "Saya") -> None:
        self.saya = saya_instance
        self.require_contents = [
            RequireContext("graia.saya.__special__.global_behaviours", [])
        ]

    @property
    def currentModule(self):
        return self.require_contents[-1].module

    @property
    def _index(self):
        return self.require_contents[-1]._index

    def require_context(self, module: str, behaviours: List["Behaviour"] = None):
        self.require_contents.append(RequireContext(module, behaviours or []))
        return self

    def __enter__(self) -> "BehaviourInterface":
        return self

    def __exit__(self, _, exc: Exception, tb):
        self.require_contents.pop()  # just simple.
        if tb is not None:
            raise exc.with_traceback(tb)

    def behaviour_generator(self):
        yield from self.require_contents[0].behaviours
        # Cube 没有 behaviours 设定, 哦, 连 always 都没有.
        yield from self.require_contents[-1].behaviours

    def allocate_cube(self, cube: Cube) -> Any:
        start_offset = self._index + int(bool(self._index))

        for self.require_contents[-1]._index, behaviour in enumerate(
            itertools.islice(self.behaviour_generator(), start_offset, None, None),
            start=start_offset,
        ):
            result = behaviour.allocate(cube)

            if result is None:
                continue

            self.require_contents[-1]._index = 0
            return result
        else:
            raise RequirementCrashed(f"the dispatching requirement crashed: {cube}")

    def uninstall_cube(self, cube: Cube) -> Any:
        start_offset = self._index + int(bool(self._index))

        for self.require_contents[-1]._index, behaviour in enumerate(
            itertools.islice(self.behaviour_generator(), start_offset, None, None),
            start=start_offset,
        ):
            result = behaviour.uninstall(cube)

            if result is None:
                continue

            self.require_contents[-1]._index = 0
            return result
        else:
            raise RequirementCrashed(f"the dispatching requirement crashed: {cube}")
