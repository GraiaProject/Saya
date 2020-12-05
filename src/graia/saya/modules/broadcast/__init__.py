from typing import Callable, Hashable, List, Optional, Type
from graia.broadcast.entities.decorater import Decorater
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import BaseEvent
from graia.broadcast.entities.listener import Listener
from graia.broadcast.entities.namespace import Namespace
from graia.saya.entities.behaviour import Behaviour
from graia.broadcast import Broadcast

from graia.saya.entities.cube import Cube
from graia.saya.entities.isolate import Isolate
from graia.saya.entities.schema import Schema

class ListenerSchema(Schema, Listener):
    require_behaviours = ["BroadcastBehaviour"]

    __init__ = Listener.__init__

class ListenerCube(Cube[Listener, ListenerSchema]):
    def __init__(self, schema: ListenerSchema) -> None:
        super().__init__(schema)
    
    def getUniqueKey(self) -> Hashable:
        if self.content is None:
            raise ValueError("content hasn't been inited.")
        return self.content

class BroadcastIsolate(Isolate[Namespace]):
    def __init__(self, name: str, priority: int, injected_dispatchers: List[BaseDispatcher] = None) -> None:
        self.layer = Namespace(
            name=name, priority=priority,
            injected_dispatchers=injected_dispatchers or []
        )

class BroadcastBehaviour(Behaviour):
    broadcast: Broadcast

    def __init__(self, broadcast: Broadcast) -> None:
        self.broadcast = broadcast
        super().__init__()
    
    def mountCube(self, cube: "ListenerCube", using_isolates: Optional["BroadcastIsolate"] = None):
        if using_isolates is not None:
            self.manage_isolates.setdefault(using_isolates, [])
            if cube in self.manage_isolates[using_isolates]:
                raise ValueError("the same cube has been the using isolate.")
            self.manage_isolates[using_isolates].append(cube)
        
        self.manage_cubes.append(cube)
        listener = Listener(
            callable=cube.schema.callable,
            namespace=using_isolates.layer if using_isolates else self.broadcast.getDefaultNamespace(),
            inline_dispatchers=cube.schema.inline_dispatchers,
            priority=cube.schema.priority,
            listening_events=cube.schema.listening_events,
            headless_decoraters=cube.schema.headless_decoraters,
            enable_internal_access=cube.schema.enable_internal_access
        )
        self.broadcast.listeners.append(listener)
        cube.setContent(listener)
    
    def unmountCube(self, cube: "ListenerCube"):
        self.broadcast.removeListener(cube.content)
        self.manage_cubes.remove(cube)
        for isolate_part in self.manage_isolates.values():
            if cube in isolate_part:
                isolate_part.remove(cube)
        
        cube.unsetContent()
    
