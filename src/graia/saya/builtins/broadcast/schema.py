from dataclasses import dataclass, field
from typing import Callable, List, Optional, Type

from graia.broadcast import Broadcast
from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.entities.listener import Listener
from graia.broadcast.entities.namespace import Namespace
from graia.broadcast.typing import T_Dispatcher

from graia.saya.schema import BaseSchema


@dataclass
class ListenerSchema(BaseSchema):
    listening_events: List[Type[Dispatchable]]
    namespace: Optional[Namespace] = None
    inline_dispatchers: List[T_Dispatcher] = field(default_factory=list)
    decorators: List[Decorator] = field(default_factory=list)
    priority: int = 16

    def build_listener(self, callable: Callable, broadcast: "Broadcast"):
        return Listener(
            callable=callable,
            namespace=self.namespace or broadcast.getDefaultNamespace(),
            listening_events=self.listening_events,
            inline_dispatchers=self.inline_dispatchers,
            decorators=self.decorators,
            priority=self.priority,
        )
