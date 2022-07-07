from dataclasses import dataclass, field
from enum import Enum
from tkinter.messagebox import NO


class Gender(Enum):
    Male = "M"
    Female = "F"
    Null = ""


class Modifier(Enum):
    X_MegaEvolution = "MX"
    Y_MegaEvolution = "MY"
    UnknownModifier1 = "R"
    Null = ""


@dataclass
class ModifierGroup:
    modifiers: list[Modifier]

    def toString(self) -> str:
        modifiers = ""
        for mod in self.modifiers:
            modifiers+=mod.value
        return modifiers


@dataclass
class Sprite:
    dexNumber: int
    generation: int
    gameTitle: str
    isBackSprite: bool = False
    gender: Gender = Gender.Null
    isShiny: bool = False
    modifier: Modifier = Modifier.Null
    name: str = None
    imageData: bytes = None
    #  modifiers: ModifierGroup = field(default_factory=list)
