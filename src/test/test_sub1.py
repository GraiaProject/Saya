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
    listening_events=[SayaModuleInstalled, SayaModuleUninstalled, SayaModuleUninstall]
))
async def install_hook():
    logger.debug("test sub1 installed!")