from importlib import reload
from typing import List, Optional, Sequence, Set, Type

from graia.saya.entities.behaviour import Behaviour
from graia.saya.entities.cube import Cube
from graia.saya.entities.isolate import Isolate
from graia.saya.entities.schema import Schema
from graia.saya.entities.various import MountVarious, UnmountVarious

def event_class_generator(target):
    for i in target.__subclasses__():
        yield i
        if i.__subclasses__():
            yield from event_class_generator(i)

def findBehaviour(name: str):
    for i in event_class_generator(Behaviour):
      if i.__name__ == name:
        return i

class Saya:
    behaviours: List[Behaviour]

    def __init__(self) -> None:
        self.behaviours = []

    @property
    def behaviour_types(self) -> Set[Type[Behaviour]]:
        return set(i.__class__ for i in self.behaviours)

    def hasBehaviours(self, *behaviour_types: Type[Behaviour]):
        return set(behaviour_types).issubset(self.behaviour_types)
    
    def registerBehaviour(self, behaviour: Behaviour) -> None:
        if behaviour.__class__ in self.behaviour_types:
            raise TypeError("behavior executor conflict")

        self.behaviours.append(behaviour)
    
    def removeBehaviour(self, behaviour: Behaviour) -> None:
        if behaviour.manage_cubes:
            raise ValueError("this behaviour must has no any cube.")

        if behaviour not in self.behaviours:
            raise ValueError("this behaviour hasn't been registered.")

        self.behaviours.remove(behaviour)
    
    def installCube(self, cube: Cube, using_isolates: Optional["Isolate"] = None) -> None:
        require_set = set([i if i.__class__ is not str else findBehaviour(i) for i in cube.schema.require_behaviours])
        if not require_set.issubset(self.behaviour_types):
            raise TypeError("detected unexpected unregistered behaviour: {0}".format(
                ", ".join(list(require_set.difference(self.behaviour_types)))
            ))
        
        for behaviour in list(filter(lambda x: x.__class__ in require_set, self.behaviours)):
            if cube in behaviour.manage_cubes:
                raise ValueError("detected managing cube in {0}".format(behaviour))
            behaviour.mountCube(cube, using_isolates)
            cube.onMount(MountVarious.Install)
    
    def uninstallCube(self, cube: Cube) -> None:
        require_set = set([i if i.__class__ is not str else findBehaviour(i) for i in cube.schema.require_behaviours])
        for behaviour in list(filter(lambda x: x.__class__ in require_set, self.behaviours)):
            if cube not in behaviour.manage_cubes:
                raise TypeError("detected an unexpected lost cube [{0}] in behaviour [{1}]".format(cube, behaviour))
            cube.beforeUnmount(UnmountVarious.Uninstall)
            behaviour.unmountCube(cube)
    
    def installCubes(self, cube_seq: Sequence[Cube], using_isolates: Optional["Isolate"] = None) -> None:
        for i in cube_seq:
            self.installCube(i, using_isolates)
    
    def uninstallCubes(self, cube_seq: Sequence[Cube]) -> None:
        for i in cube_seq:
            self.uninstallCube(i)
    
    