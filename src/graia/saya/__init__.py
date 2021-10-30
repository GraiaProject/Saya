import asyncio
import copy
import importlib
import sys
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, NoReturn, Optional, Union

from graia.broadcast import Broadcast
from loguru import logger

from graia.saya.behaviour import Behaviour, BehaviourInterface
from graia.saya.channel import Channel
from graia.saya.cube import Cube
from graia.saya.schema import BaseSchema

from .context import channel_instance, environment_metadata, saya_instance


class Saya:
    """Modular application for Graia Framework.

    > 名称取自作品 魔女之旅 中的角色 "沙耶(Saya)", 愿所有人的心中都有一位活泼可爱的炭之魔女.

    Saya 的架构分为: `Saya Controller`(控制器), `Module Channel`(模块容器), `Cube`(内容容器), `Behaviour`(行为).

     - `Saya Controller` 负责管理各个模块的引入, 即本 `Saya` 类
     - `Module Channel` 负责在模块内收集组件信息
     - `Cube` 则用于使用 `Schema` 构造的元信息实例去描述内容
     - `Behaviour` 用于通过对 `Cube` 内的元信息进行解析, 并提供对其他已有接口的 Native 支持
    """

    behaviour_interface: BehaviourInterface
    behaviours: List[Behaviour]
    channels: Dict[str, Channel]
    broadcast: Optional[Broadcast] = None

    mounts: Dict[str, Any]

    def __init__(self, broadcast: Broadcast = None) -> None:
        self.channels = {}
        self.behaviours = []
        self.behaviour_interface = BehaviourInterface(self)
        self.behaviour_interface.require_contents[0].behaviours = self.behaviours

        self.mounts = {}
        self.broadcast = broadcast

    @contextmanager
    def module_context(self):
        saya_token = saya_instance.set(self)
        yield
        saya_instance.reset(saya_token)

    @staticmethod
    def current() -> "Saya":
        """返回当前上下文中的 Saya 实例

        Returns:
            Saya: 当前上下文中的 Saya 实例
        """
        return saya_instance.get()

    def require_resolve(self, module: str) -> Channel:
        """导入模块, 并注入 Channel, 模块完成内容注册后返回该 Channel

        Args:
            module (str): 需为可被当前运行时访问的 Python Module 的引入路径

        Returns:
            Channel: 已注册了内容的 Channel.
        """
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
                        logger.exception(
                            f"an error occurred while loading the module's cube: {module}::{cube}"
                        )
                        raise
        finally:
            channel_instance.reset(channel_token)

        return channel

    @staticmethod
    def current_env() -> Any:
        """只能用于模块内. 返回在调用 Saya.require 方法时传入的 `require_env` 参数的值

        Returns:
            Any: 在调用 Saya.require 方法时传入的 `require_env` 参数的值
        """
        return environment_metadata.get(None)

    def require(self, module: str, require_env: Any = None) -> Union[Channel, Any]:
        """既处理 Channel, 也处理 Channel 中的 export 返回

        Args:
            module (str): 需为可被当前运行时访问的 Python Module 的引入路径
            require_env (Any, optional): 可以把这个参数作为硬编码配置使用, 虽然应该是叫传入 "环境条件".

        Returns:
            Union[Channel, Any]: 大多数情况下应该是 Channel, 如果设定了 export 就不一样了
        """
        logger.debug(f"require {module}")

        if module in self.channels:
            channel = self.channels[module]
            if channel._export:
                return channel._export
            return channel

        env_token = environment_metadata.set(require_env)
        channel = self.require_resolve(module)
        self.channels[module] = channel
        environment_metadata.reset(env_token)

        if self.broadcast:
            token = saya_instance.set(self)
            self.broadcast.postEvent(
                SayaModuleInstalled(
                    module=module,
                    channel=channel,
                )
            )
            saya_instance.reset(token)

        logger.info(f"module loading finished: {module}")

        if channel._export:
            return channel._export

        return channel

    def install_behaviours(self, *behaviours: Behaviour):
        """在控制器中注册 Behaviour, 用于处理模块提供的内容"""
        self.behaviours.extend(behaviours)

    def uninstall_channel(self, channel: Channel):
        """卸载指定的 Channel

        Args:
            channel (Channel): 需要卸载的 Channel

        Raises:
            TypeError: 提供的 Channel 不在本 Saya 实例内
            ValueError: 尝试卸载 __main__, 即主程序所属的模块
        """
        if channel not in self.channels.values():
            raise TypeError("assert an existed channel")

        if channel.module == "__main__":
            raise ValueError("main channel cannot uninstall")

        # TODO: builtin signal(async or sync)
        if self.broadcast:
            token = saya_instance.set(self)
            self.broadcast.postEvent(
                SayaModuleUninstall(
                    module=channel.module,
                    channel=channel,
                )
            )
            saya_instance.reset(token)

        with self.behaviour_interface.require_context(channel.module) as interface:
            for cube in channel.content:
                try:
                    interface.uninstall_cube(cube)
                except:
                    logger.exception(
                        f"an error occurred while loading the module's cube: {channel.module}::{cube}"
                    )
                    raise

        del self.channels[channel.module]
        channel._py_module = None

        if sys.modules.get(channel.module):
            del sys.modules[channel.module]

        if self.broadcast:
            token = saya_instance.set(self)
            self.broadcast.postEvent(
                SayaModuleUninstalled(
                    module=channel.module,
                )
            )
            saya_instance.reset(token)

    def reload_channel(self, channel: Channel) -> None:
        """重载指定的模块

        Args:
            channel (Channel): 指定需要重载的模块, 请使用 channels.get 方法获取

        Raises:
            TypeError: 没有给定需要被重载的模块(`channel` 与 `module` 都不给定)
            ValueError: 没有通过 `module` 找到对应的 Channel
        """
        self.uninstall_channel(channel)
        new_channel: Channel = self.require_resolve(channel.module)

        channel._name = new_channel._name
        channel._author = new_channel._author
        channel._description = new_channel._description
        channel._export = new_channel._export
        channel._py_module = new_channel._py_module
        channel.content = new_channel.content

        self.channels[channel.module] = channel

    def create_main_channel(self) -> Channel:
        """创建不可被卸载的 `__main__` 主程序模块

        Returns:
            Channel: 属性 `name` 值为 `__main__`, 且无法被 `uninstall_channel` 卸载的模块.
        """
        may_current = self.channels.get("__main__")
        if may_current:
            return may_current

        main_channel = Channel("__main__")
        self.channels["__main__"] = main_channel

        if self.broadcast:
            token = saya_instance.set(self)
            self.broadcast.postEvent(
                SayaModuleInstalled(
                    module="__main__",
                    channel=main_channel,
                )
            )
            saya_instance.reset(token)

        return main_channel

    def mount(self, mount_point: str, target):
        """挂载实例到 Saya 下, 以便整个模块系统共用.

        Args:
            mount_point (str): 指定的挂载点, 建议使用类似 `saya.builtin.asyncio.event_loop` 这样的形式
            target (Any): 需要挂载的实例

        Returns:
            NoReturn: 已将实例挂载, 可能把已经注册的挂载点给覆盖了.
        """
        self.mounts[mount_point] = target

    def unmount(self, mount_point: str):
        """删除挂载及其挂载点

        Args:
            mount_point (str): 目标挂载点

        Returns:
            NoReturn: 已经删除

        Raises:
            KeyError: 挂载点不存在
        """
        del self.mounts[mount_point]

    def access(self, mount_point: str):
        """访问特定挂载点

        Args:
            mount_point (str): 目标挂载点

        Returns:
            Any: 已经挂载的实例

        Raises:
            KeyError: 挂载点不存在
        """
        return self.mounts[mount_point]


from .event import SayaModuleInstalled, SayaModuleUninstall, SayaModuleUninstalled
