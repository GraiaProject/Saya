import asyncio

from graia.saya import Saya
from graia.broadcast import Broadcast
from graia.saya.builtins.broadcast import BroadcastBehaviour

loop = asyncio.get_event_loop()
broadcast = Broadcast(loop=loop)
saya = Saya(broadcast)

with saya.module_context():
    saya.require("modules.module_as_file")
    saya.require("modules.module_as_dir")

try:
    loop.run_forever()
except KeyboardInterrupt:
    exit()