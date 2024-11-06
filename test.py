from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.event import SayaModuleInstalled
from creart import it

saya = it(Saya)

with saya.main_context() as channel:

    @channel.scoped_context
    class context1:
        a: str

        @channel.use(ListenerSchema(listening_events=[SayaModuleInstalled]))
        async def prepare(self, event: SayaModuleInstalled):
            self.a = "1"
