from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from graia.saya.channel import Channel
from graia.saya.context import saya_instance


class SayaModuleInstalled(Dispatchable):
    """不用返回 RemoveMe, 因为 Cube 在被 uninstall 时会被清理掉, 如果你用的是规范的 Saya Protocol 的话."""

    module: str
    channel: Channel

    def __init__(self, module: str, channel: Channel) -> None:
        self.module = module
        self.channel = channel

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface[SayaModuleInstalled]"):
            from graia.saya import Saya

            if interface.annotation is Saya:
                return saya_instance.get()
            elif interface.annotation is Channel:
                return interface.event.channel


class SayaModuleUninstall(Dispatchable):
    """不用返回 RemoveMe, 因为 Cube 在被 uninstall 时会被清理掉, 如果你用的是规范的 Saya Protocol 的话."""

    module: str
    channel: Channel

    def __init__(self, module: str, channel: Channel) -> None:
        self.module = module
        self.channel = channel

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface[SayaModuleUninstall]"):
            from graia.saya import Saya

            if interface.annotation is Saya:
                return saya_instance.get()
            elif interface.annotation is Channel:
                return interface.event.channel


class SayaModuleUninstalled(Dispatchable):
    """不用返回 RemoveMe, 因为 Cube 在被 uninstall 时会被清理掉, 如果你用的是规范的 Saya Protocol 的话."""

    module: str

    def __init__(self, module: str) -> None:
        self.module = module

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface[SayaModuleUninstalled]"):
            from graia.saya import Saya

            if interface.annotation is Saya:
                return saya_instance.get()
