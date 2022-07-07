import sys
from data.sprite import Gender, Modifier, Sprite

from scrapping.scrap import Scrapper
from dao.spriteDAOFromFile import spriteDAOFromFile


if __name__ == "__main__":
    # sys.path.append('./')

    mySprite = Sprite(
        dexNumber=1, 
        generation=1,
        gameTitle="red",
        isBackSprite=False,
        gender=Gender.Female,
        isShiny=True,
        modifier=Modifier.X_MegaEvolution
        #  modifiers=ModifierGroup([Modifier.X_MegaEvolution, Modifier.UnknownModifier1])
    )
    print(mySprite)

    print("scrappppppping")
    pokemonName = "charmander"
    scrapper = Scrapper()
    spriteDao = spriteDAOFromFile()
    pokemonSprites = scrapper.scrapImage(pokemonName)
    for index, sprite in enumerate(pokemonSprites):
        spriteDao.saveSpriteInFile(sprite, pokemonName, salt = str(index))
