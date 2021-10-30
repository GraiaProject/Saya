from typing import Any, Union

from graia.broadcast import Broadcast

from graia.saya.behaviour import Behaviour
from graia.saya.cube import Cube

from .schema import ListenerSchema


class BroadcastBehaviour(Behaviour):
    broadcast: Broadcast

    def __init__(self, broadcast: Broadcast) -> None:
        self.broadcast = broadcast

    def allocate(
        self,
        cube: Cube[
            Union[
                ListenerSchema,
            ]
        ],
    ):
        if isinstance(cube.metaclass, ListenerSchema):
            listener = cube.metaclass.build_listener(cube.content, self.broadcast)
            if not listener.namespace:
                listener.namespace = self.broadcast.getDefaultNamespace()
            self.broadcast.listeners.append(listener)
        else:
            return
        return True

    def uninstall(self, cube: Cube) -> Any:
        if isinstance(cube.metaclass, ListenerSchema):
            self.broadcast.removeListener(self.broadcast.getListener(cube.content))
        else:
            return

        return True
