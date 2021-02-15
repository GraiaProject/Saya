import asyncio
from typing import Any

from graia.broadcast.entities.event import BaseEvent

from graia.saya import Saya, Cube
from graia.broadcast import Broadcast
from graia.saya.behaviour import Behaviour
from graia.saya.schema import BaseSchema
from graia.saya.builtins.broadcast import BroadcastBehaviour
from . import TestSchema

class TestBehaviour(Behaviour):
    def allocate(self, content: Cube) -> Any:
        if isinstance(content.metaclass, TestSchema):
            print("cube detected", content, content.metaclass)
            return content
    
    def uninstall(self, cube: Cube) -> Any:
        return cube

loop = asyncio.get_event_loop()
broadcast = Broadcast(loop=loop)
saya = Saya(broadcast=broadcast)
saya.install_behaviours(TestBehaviour())
saya.install_behaviours(BroadcastBehaviour(broadcast))

with saya.module_context():
    test_sub1_export = saya.require("test.test_sub1")
    print(broadcast.listeners)
    saya.uninstall_channel(test_sub1_export)

async def do_nothing():
    pass

loop.run_until_complete(do_nothing())