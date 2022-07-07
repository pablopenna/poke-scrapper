from abc import ABC, abstractmethod

from data.sprite import Sprite

# DAO Interface
class SpriteDAO(ABC):

    @abstractmethod
    def read(self, pokemonName: str):
        pass

    @abstractmethod
    def write(self, sprite: Sprite):
        pass