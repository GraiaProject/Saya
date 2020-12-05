import asyncio

from graia.broadcast.entities.event import BaseEvent

from graia.saya import Saya
from graia.saya.modules.broadcast import BroadcastBehaviour, BroadcastIsolate, ListenerCube, ListenerSchema
from graia.broadcast import Broadcast

class Event1(BaseEvent):
    class Dispatcher:
        def catch(self, interface):
            pass

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
saya = Saya()
behaviour = BroadcastBehaviour(bcc)
saya.registerBehaviour(behaviour)

async def test(event: Event1):
    print("catched...", event)

cube = ListenerCube(ListenerSchema(
    test, None, [Event1]
))
isolate = BroadcastIsolate("h", 16)
saya.installCube(cube, isolate)

print(bcc.listeners[0].namespace)

#bcc.postEvent(Event1())
saya.uninstallCube(cube)
print(bcc.listeners)
print(behaviour.manage_cubes, behaviour.manage_isolates)

#loop.run_until_complete(asyncio.sleep(1))