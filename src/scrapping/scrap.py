from types import DynamicClassAttribute
from typing import Final
import re
import requests
from bs4 import BeautifulSoup

from data.sprite import Gender, Modifier, Sprite


class Scrapper:
    URL_PATTERN: Final = 'https://bulbapedia.bulbagarden.net/wiki/{pokemonName}'
    SPRITE_URL_PREFIX = '//cdn.bulbagarden.net/upload/9/9d/'
    SPRITE_URL_PATTERN = 'Spr{isBacksprite}_{generation}{title}_{dexNumber}{modifiers}{gender}{isShiny}.png'
    IMAGE_DATA_PREFIX = 'data:image/png;base64,'

    SPRITE_URL_REGEXP = re.compile('.*Spr(_b)?(_[0-9]+)([a-z]+)(_[0-9]+)([A-Z]+)?(_[mf])?(_s)?.png')

    def generateSpriteUrl(self, sprite: Sprite) -> str:
        sBacksprite = "_b" if sprite.isBackSprite else ""
        sShiny = "_s" if sprite.isShiny else ""
        sGender = "_" + sprite.gender if sprite.gender != Gender.Null else ""

        return self.SPRITE_URL_PATTERN.format(
            isBacksprite=sBacksprite, 
            generation=sprite.generation, 
            title=sprite.gameTitle, 
            dexNumber=sprite.gameTitle,
            modifiers=sprite.modifiers.toString(), 
            gender=sGender, 
            isShiny=sShiny
        )

    def parseSpriteUrl(self, spriteUrl: str) -> Sprite:
        spriteUrlExpression = self.SPRITE_URL_REGEXP.match(spriteUrl)
        matchGroups = spriteUrlExpression.groups()

        # groups[0] # (Opt.) is backsprite ("_b", None)
        # groups[1] # generation (e.g"_4")
        # groups[2] # title (e.g: "r","g","b","g","s",...)
        # groups[3] # dexNumber
        # groups[4] # (Opt.) modifiers (e.g. "R", "MX" - megaevolution in X)
        # groups[5] # (Opt.) gender ("_m","_f", None)
        # groups[6] # (Opt.) isShiny ("_s", None)

        sprite = Sprite(
            dexNumber=matchGroups[3].strip("_"),
            generation=matchGroups[1].strip("_"),
            gameTitle=matchGroups[2],
            isBackSprite=True if matchGroups[0] else False,
            gender=Gender(matchGroups[5].strip("_")).name if matchGroups[5] else Gender.Null,
            isShiny=True if matchGroups[6] else False,
            modifier=Modifier(matchGroups[4]).name if matchGroups[4] else Modifier.Null
        )

        return sprite

    def scrapImage(self, pokemonName):
        webPage = self.requestWebPage(pokemonName)
        return self.extractImagesFromWebPage(webPage)

    def requestWebPage(self, pokemonName):
        pass  # Return BeautifulSoup or null if request.status != 200
        webPageRequest = requests.get(self.URL_PATTERN.format(pokemonName=pokemonName))
        
        if webPageRequest.status_code == 200:
            webPageSoup = BeautifulSoup(webPageRequest.content, 'html.parser')
            return webPageSoup
        else:
            return None


    def extractImagesFromWebPage(self, webPageSoup):
        pokemonName = webPageSoup.find(id="firstHeading").contents[0]
        imageUrls = webPageSoup.find_all('img', {'src': self.SPRITE_URL_REGEXP})
        if len(imageUrls) == 0:
            print("No sprites found!")
            return

        sprites = []
        for idx, imageTag in enumerate(imageUrls):
            print(str(idx) + "\t| " + imageTag["alt"])
            imageRequest = requests.get("https:" + imageTag["src"])
            #  print(imageRequest.content)
            imageData = imageRequest.content

            sprite = self.parseSpriteUrl(imageTag["src"])
            sprite.imageData = imageData
            sprite.name = pokemonName
            sprites.append(sprite)
        
        return sprites


