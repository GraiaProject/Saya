from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.event import SayaModuleInstalled, SayaModuleUninstall, SayaModuleUninstalled
from . import TestSchema
from loguru import logger

saya = Saya.current()
channel = Channel.current()

@channel.use(TestSchema(test_name="1"))
def cube_content(a, b, c):
    return sum([a, b, c])

@channel.use(ListenerSchema(
    listening_events=[SayaModuleInstalled, SayaModuleUninstalled, SayaModuleUninstall],
    enable_internal_access=True
))
async def install_hook(interface: DispatcherInterface):
    if interface.event.module == __name__:
        print("test sub1:", interface.event.__class__.__name__, interface.event)

print("我被执行了一次.")