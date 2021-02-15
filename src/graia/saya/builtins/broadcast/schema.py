from dataclasses import dataclass, field
from typing import Callable, List, Type
from graia.broadcast import Listener, BaseEvent, BaseDispatcher
from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.entities.namespace import Namespace
from graia.saya.schema import BaseSchema

@dataclass
class ListenerSchema(BaseSchema):
    listening_events: List[Type[BaseEvent]]
    namespace: Namespace = None
    inline_dispatchers: List[BaseDispatcher] = field(default_factory=list)
    headless_decorators: List[Decorator] = field(default_factory=list)
    priority: int = 16
    enable_internal_access: bool = False

    def build_listener(self, callable: Callable):
        return Listener(
            callable=callable,
            namespace=self.namespace,
            listening_events=self.listening_events,
            inline_dispatchers=self.inline_dispatchers,
            headless_decorators=self.headless_decorators,
            priority=self.priority,
            enable_internal_access=self.enable_internal_access
        )