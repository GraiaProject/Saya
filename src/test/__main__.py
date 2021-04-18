import asyncio
from typing import Any

from graia.broadcast.entities.event import BaseEvent
from pydantic.main import BaseModel

from graia.saya import Saya, Cube
from graia.broadcast import Broadcast
from graia.saya.behaviour import Behaviour
from graia.saya.behaviour.builtin import MountPoint
from graia.saya.behaviour.entity import Router
from graia.saya.config.interface import SayaConfigInterface
from graia.saya.schema import BaseSchema
from graia.saya.builtins.broadcast import BroadcastBehaviour
from . import TestSchema

class TestBehaviour(Behaviour):
    def allocate(self, content: Cube) -> Any:
        if isinstance(content.metaclass, TestSchema):
            #print("cube detected", content, content.metaclass)
            return content
    
    def uninstall(self, cube: Cube) -> Any:
        return cube

class TestRouter(Router):
    def route(self, route: str) -> Any:
        if route == "route_test":
            return 1

loop = asyncio.get_event_loop()
broadcast = Broadcast(loop=loop)
saya = Saya(broadcast=broadcast)
saya.install_behaviours(TestBehaviour())
saya.install_behaviours(BroadcastBehaviour(broadcast))
saya.install_behaviours(SayaConfigInterface("./testconfig").build_mount_point("config.global"))

class TestModel(BaseModel):
    field1: int
    field2: str

with saya.module_context():
    test_sub1_channel = saya.require("test.test_sub1")
    print("尝试直接 require:", saya.require("test.test_sub1"))
    print("====================")
    saya.reload_channel(test_sub1_channel)
    print("通过 reload:", test_sub1_channel)
    print("reload 后 channels:", saya.channels)
    print("再次尝试直接 require:", saya.require("test.test_sub1"))
    print("测试 SCI 加载:", saya.find_route("config.global").config_tree)
    config_result: TestModel = saya.find_route("config.global").build_config_model(TestModel)
    print("测试 SCI 的 build:", config_result.field2)

async def do_nothing():
    pass

loop.run_until_complete(do_nothing())