import os
from dao.spriteDAO import SpriteDAO
from data.sprite import Sprite

class spriteDAOFromFile(SpriteDAO):
    
    def read():
        pass

    def write():
        pass

    def saveSpriteInFile(self, sprite: Sprite, bOverwrite: bool = False, salt: str = ""):
        
        saveDirPath = os.path.dirname(__file__) + "/../../img/"
        saveDirPath += sprite.dexNumber + "/"
        try:
            os.mkdir(saveDirPath)
        except:
            pass

        filePath = saveDirPath + self.__fileNameForSprite(sprite, salt)
        fileFlag = 'wb' if bOverwrite else 'xb'
        
        print("Writing in {}".format(filePath))
        
        try:
            with open(filePath, fileFlag) as f:
                if sprite.imageData != None:
                    f.write(sprite.imageData)
                else:
                    print("Sprite has no image data!")
        except Exception as ex:
            print("Could not write on {}. ERROR: {}".format(filePath, ex))

    def __fileNameForSprite(self, sprite: Sprite, salt) -> str:
        backspriteLabel = "b" if sprite.isBackSprite else ""
        shinyLabel = "s" if sprite.isShiny else ""
        return sprite.name + "__" + sprite.dexNumber + "_" + sprite.generation + sprite.gameTitle + "_" + sprite.gender.value + backspriteLabel + shinyLabel + sprite.modifier.value + "{}.png".format(salt)