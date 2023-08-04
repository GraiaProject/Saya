from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from creart import AbstractCreator, CreateTargetInfo, exists_module, it

from . import Saya

if TYPE_CHECKING:
    from .builtins.broadcast import BroadcastBehaviour


class SayaCreator(AbstractCreator):
    targets = (
        CreateTargetInfo(
            module="graia.saya",
            identify="Saya",
            humanized_name="Saya",
            description="<common,graia,saya> a modular implementation with modern design and injection",
            author=["GraiaProject@github"],
        ),
    )

    @staticmethod
    def create(create_type: type[Saya]) -> Saya:
        try:
            from graia.broadcast import Broadcast

            from .builtins.broadcast import BroadcastBehaviour

            broadcast = it(Broadcast)
            saya = create_type(broadcast)
            saya.install_behaviours(it(BroadcastBehaviour))
        except (ImportError, TypeError):
            saya = create_type()

        with suppress(ImportError, TypeError):
            from graia.scheduler.saya.behaviour import GraiaSchedulerBehaviour

            saya.install_behaviours(it(GraiaSchedulerBehaviour))

        return saya


class BroadcastBehaviourCreator(AbstractCreator):
    targets = (
        CreateTargetInfo(
            "graia.saya.builtins.broadcast.behaviour", "BroadcastBehaviour"
        ),
    )

    @staticmethod
    def available() -> bool:
        return exists_module("graia.broadcast")

    @staticmethod
    def create(create_type: type[BroadcastBehaviour]) -> BroadcastBehaviour:
        from graia.broadcast import Broadcast

        broadcast = it(Broadcast)
        return create_type(broadcast)
