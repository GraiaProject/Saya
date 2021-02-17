from graia.broadcast.entities.event import BaseEvent
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from graia.saya.channel import Channel
from graia.saya.context import saya_instance
from typing import TYPE_CHECKING


class SayaModuleInstalled(BaseEvent):
    """不用返回 RemoveMe, 因为 Cube 在被 uninstall 时会被清理掉, 如果你用的是规范的 Saya Protocol 的话.
    """
    module: str
    channel: Channel

    class Dispatcher(BaseDispatcher):
        async def catch(interface: "DispatcherInterface"):
            from graia.saya import Saya

            if interface.annotation is Saya:
                return saya_instance.get()
            elif interface.annotation is Channel:
                return interface.event.channel

class SayaModuleUninstall(BaseEvent):
    """不用返回 RemoveMe, 因为 Cube 在被 uninstall 时会被清理掉, 如果你用的是规范的 Saya Protocol 的话.
    """
    module: str
    channel: Channel

    class Dispatcher(BaseDispatcher):
        async def catch(interface: "DispatcherInterface"):
            from graia.saya import Saya

            if interface.annotation is Saya:
                return saya_instance.get()
            elif interface.annotation is Channel:
                return interface.event.channel

class SayaModuleUninstalled(BaseEvent):
    """不用返回 RemoveMe, 因为 Cube 在被 uninstall 时会被清理掉, 如果你用的是规范的 Saya Protocol 的话.
    """
    module: str

    class Dispatcher(BaseDispatcher):
        async def catch(interface: "DispatcherInterface"):
            from graia.saya import Saya

            if interface.annotation is Saya:
                return saya_instance.get()
            elif interface.annotation is Channel:
                return interface.event.channel