import enum

class MountVarious(enum.IntEnum):
    Install = 0 # Cube 被引入当前应用实例(offer: Saya)
    Enable = 1 # Cube 被启用, 之前被禁用(offer: external)
    Unhide = 2 # Cube 被设为显式, 之前为隐式(offer: external)

class UnmountVarious(enum.IntEnum):
    Uninstall = 0
    Disable = 1
    Hide = 2

