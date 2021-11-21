<div align="center">

# Saya

_a modular implementation with modern design and injection_ 

> 不仅仅是模块化, 就如炭之魔女不仅仅只有追求心上人的一面.
>  

</div>

## Installation

```bash
pip install graia-saya
```

或者使用 `poetry` :

```bash
poetry add graia-saya
```

## 架构简述

Saya 的架构分为这几大块: `Saya Controller` (控制器), `Module Channel` (模块容器), `Cube` (内容容器), `Schema` (元信息模板), `Behaviour` (行为).

 - `Saya Controller` : 负责控制各个模块, 分配 `Channel` , 管理模块启停, `Behaviour` 的注册和调用.
 - `Module Channel` : 负责对模块服务, 收集模块的各式信息, 像 模块的名称, 作者, 长段的描述 之类, 
 并负责包装模块的内容为 `Cube` , 用以 `Behaviour` 对底层接口的操作.
 - `Cube` : 对模块提供的内容附加一个由 `Schema` 实例化来的 `metadata` , 即 "元信息", 用于给 `Behaviour` 进行处理.
 - `Schema` : 用于给模块提供的内容附加不同类型的元信息, 给 `Behaviour`  `isinstance` 处理用.
 - `Behaviour` : 根据 `Cube` 及其元信息, 对底层接口(例如 `Broadcast` , `Scheduler` 等)进行操作.
 包括 `allocate` 与 `uninstall` 两个操作.

## 使用

安装后, 在编辑器内打开工作区, 创建如下的目录结构:

这里我们建立的是 Real World 中的, 最简且最易于扩展, 维护的 **示例性** 目录结构.  
`Saya` 中, 我们的导入机制复用了 Python 自身的模块和包机制, 理论上只需要符合 Python 的导入规则, 
就能引入模块到实例中.

```bash
/home/elaina/saya-example
│  .gitignore
│  main.py
│  pyproject.toml
│
└─ modules
    │  __init__.py
    │  module_as_file.py # 作为文件的合法模块可以被调用.
    │
    └─ module_as_dir # 作为文件夹的合法模块可以被调用(仅调用 __init__.py 下的内容).
            __init__.py
```

`Saya` 需要一个入口( `entry` ), 用于创建 `Controller` , 并让 `Controller` 分配 `Channel` 给这之后被 `Saya.require` 方法引入的模块.
在我们提供的目录结构中, `main.py` 将作为入口文件, 被 Python 解释器首先执行.

### 入口文件的编写

首先, 我们需要引入 `Saya` , `Broadcast` , 还有其内部集成的对 `Broadcast` 的支持:

```py
from graia.saya import Saya
from graia.broadcast import Broadcast
from graia.saya.builtins.broadcast import BroadcastBehaviour
```

分别创建 `Broadcast` , `Saya` 的实例:

```py
import asyncio

loop = asyncio.get_event_loop()
broadcast = Broadcast(loop=loop)
saya = Saya(broadcast) # 这里可以置空, 但是会丢失 Lifecycle 特性
```

创建 `BroadcastBehaviour` 的实例, 并将其注册到现有的 `Saya` 实例中:

```py
saya.install_behaviours(BroadcastBehaviour(broadcast))
```

为了导入各个模块, `Saya Controller` 需要先进入上下文:

```py
with saya.module_context():
    ...
```

引入各个模块, 这里的模块目前都需要手动引入, 后期可能会加入配置系统:

```py
with saya.module_context():
    saya.require("modules.module_as_file")
    saya.require("modules.module_as_dir")
```

这里使用传统方式启动 `asyncio` 的事件循环.

> 不同框架有不同的启动方式, 比如 Avilla 使用了 Launch Component, 这里仅做演示.

```py
try:
    loop.run_forever()
except KeyboardInterrupt:
    exit()
```

或者也可以这样:

```py
async def do_nothing():
    pass

loop.run_until_complete(do_nothing())
```

最终的结果:

```py title="Result of main.py"
import asyncio

from graia.saya import Saya
from graia.broadcast import Broadcast
from graia.saya.builtins.broadcast import BroadcastBehaviour

loop = asyncio.get_event_loop()
broadcast = Broadcast(loop=loop)
saya = Saya(broadcast)
saya.install_behaviours(BroadcastBehaviour(broadcast))

with saya.module_context():

    saya.require("modules.module_as_file")
    saya.require("modules.module_as_dir")

try:

    loop.run_forever()

except KeyboardInterrupt:

    exit()

```

就这样, 一个入口文件就这样完成了, 现在主要是插件部分.

## 第一次

来到 `module_as_file.py`:

```py
from graia.saya import Saya, Channel

saya = Saya.current()
channel = Channel.current()
```

两个 `currnet` 方法的调用, 访问了 `Saya` 实例和当前上下文分配的 `Channel` .

接下来, 导入 `ListenerSchema` :

```py
from graia.saya.builtins.broadcast.schema import ListenerSchema
```

`ListenerSchema` 作为 `Schema` , 标识相对应的模块内容为一 `Listener` , 
并在模块被导入后经由 `Behaviour` 进行操作.

使用 `Channel.use` 方法, 向 `Channel` 提供内容:

```py
@channel.use(ListenerSchema(
    listening_events=[...] # 填入你需要监听的事件
))
async def module_listener():
    print("事件被触发!!!!")
```

然后, 引入结束, `module_as_file.py` 文件内容如下, 这里我们监听 `SayaModuleInstalled` 事件, 作为 `Lifecycle API` 的简单示例:

```py title="Result of module_as_file.py"
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.event import SayaModuleInstalled

saya = Saya.current()
channel = Channel.current()

@channel.use(ListenerSchema(

    listening_events=[SayaModuleInstalled]

))
async def module_listener(event: SayaModuleInstalled):

    print(f"{event.module}::模块加载成功!!!")

```

我们对 `modules/module_as_dir/__init__.py` 也如法炮制, copy 上方的代码, 进入虚拟环境, 然后运行 `main.py`.

```bash
root@localhost: # python main.py
2021-02-16 01:19:56.632 | DEBUG    | graia.saya:require:58 - require modules.module_as_file
2021-02-16 01:19:56.639 | DEBUG    | graia.saya:require:58 - require modules.module_as_dir
modules.module_as_file::模块加载成功!!!
modules.module_as_file::模块加载成功!!!
modules.module_as_dir::模块加载成功!!!
modules.module_as_dir::模块加载成功!!!
```

## 协议

本项目使用 MIT 作为开源协议.
