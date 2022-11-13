from typing import TYPE_CHECKING

from .context import channel_instance

if TYPE_CHECKING:
    from .channel import Channel


class BaseSchema:
    channel: "Channel"

    def __post_init__(self):
        self.channel = channel_instance.get()
