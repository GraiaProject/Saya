import sys
import asyncio
import importlib
from typing import Any, Dict, List, NoReturn, Optional, Union
from contextlib import contextmanager

from graia.saya.channel import Channel

from graia.saya.schema import BaseSchema
from graia.saya.cube import Cube
from graia.saya.behaviour import Behaviour, BehaviourInterface
from graia.broadcast import Broadcast
from .context import saya_instance, channel_instance
from loguru import logger

class Saya:
    """Modular application for Graia Framework.

    > 名称取自作品 魔女之旅 中的角色 "沙耶(Saya)", 愿所有人的心中都有一位活泼可爱的炭之魔女.

    Saya 的架构分为: `Saya Controller`(控制器), `Module Channel`(模块容器), `Cube`(内容容器), `Behaviour`(行为).

     - `Saya Controller` 负责管理各个模块的

    Raises:
        TypeError: [description]

    Returns:
        [type]: [description]
    """
    behaviour_interface: BehaviourInterface
    behaviours: List[Behaviour]
    channels: List[Channel]
    broadcast: Optional[Broadcast] = None

    def __init__(self, broadcast: Broadcast = None) -> None:
        self.channels = []
        self.behaviours = []
        self.behaviour_interface = BehaviourInterface(self)
        self.behaviour_interface.require_contents[0].behaviours = self.behaviours

        self.broadcast = broadcast
    
    @contextmanager
    def module_context(self):
        saya_token = saya_instance.set(self)
        yield
        saya_instance.reset(saya_token)

    @staticmethod
    def current() -> "Saya":
        return saya_instance.get()

    @property
    def alive_channel_name_mapping(self) -> Dict[str, Channel]:
        return {i.module: i for i in self.channels}

    def require(self, module: str) -> Union[Channel, Any]:
        logger.debug(f"require {module}")

        if module in self.alive_channel_name_mapping:
            return self.alive_channel_name_mapping[module]

        channel = Channel(module)
        channel_token = channel_instance.set(channel)

        try:
            imported_module = importlib.import_module(module, module)
            channel._py_module = imported_module
            with self.behaviour_interface.require_context(module) as interface:
                for cube in channel.content:
                    try:
                        interface.allocate_cube(cube)
                    except:
                        logger.exception(f"an error occurred while loading the module's cube: {module}::{cube}")
                        raise
        finally:
            channel_instance.reset(channel_token)

        self.channels.append(channel)

        if self.broadcast:
            token = saya_instance.set(self)
            self.broadcast.postEvent(SayaModuleInstalled(
                module=module,
                channel=channel,
            ))
            saya_instance.reset(token)

        return channel
    
    def exec_module_function(self, function_name, *args, **kwargs):
        for channel in self.channels:
            potential = getattr(channel._py_module, function_name, None)
            if potential is not None and callable(potential):
                try:
                    potential(self, channel, *args, **kwargs)
                except:
                    logger.exception(f"error on executing function {channel}::{potential}")
    
    def install_behaviours(self, *behaviours: Behaviour):
        self.behaviours.extend(behaviours)
    
    def uninstall_channel(self, channel: Channel):
        if channel not in self.channels:
            raise TypeError("assert an existed channel")
        
        if channel.module == "__main__":
            raise ValueError("main channel cannot uninstall")

        # TODO: builtin signal(async or sync)
        if self.broadcast:
            token = saya_instance.set(self)
            self.broadcast.postEvent(SayaModuleUninstall(
                module=channel.module,
                channel=channel,
            ))
            saya_instance.reset(token)

        with self.behaviour_interface.require_context(channel.module) as interface:
            for cube in channel.content:
                try:
                    interface.uninstall_cube(cube)
                except:
                    logger.exception(f"an error occurred while loading the module's cube: {channel.module}::{cube}")
                    raise
        
        self.channels.remove(channel)

        for var_name in dir(channel._py_module):
            if not var_name.startswith('__'):
                channel._py_module.__dict__.clear()

        if sys.modules.get(channel.module):
            del sys.modules[channel.module]

        if self.broadcast:
            token = saya_instance.set(self)
            self.broadcast.postEvent(SayaModuleUninstalled(
                module=channel.module,
            ))
            saya_instance.reset(token)
    
    def reload_channel(self, channel: Channel):
        attr_list = ['_name', '_author', '_description', 'export']

        self.uninstall_channel(channel)
        new_channel = self.require(channel.module)
        for attr in attr_list:
            try:
                new_channel.attr = channel.attr
            except AttributeError:
                continue
        return new_channel
    
    def create_main_channel(self) -> Channel:
        may_current = self.alive_channel_name_mapping.get("__main__")
        if may_current:
            return may_current
        main_channel = Channel("__main__")
        self.channels.append(main_channel)
        
        if self.broadcast:
            token = saya_instance.set(self)
            self.broadcast.postEvent(SayaModuleInstalled(
                module="__main__",
                channel=main_channel,
            ))
            saya_instance.reset(token)
        
        return main_channel

from .event import SayaModuleInstalled, SayaModuleUninstall, SayaModuleUninstalled