import requests
from bs4 import BeautifulSoup

import argparse # lib for parsing command parameters
import os # to get file path and be able to store images always in the img/ folder

def getSprite(dexNumber, generation, title, isBacksprite, isShiny, isAlter):
    _isBacksprite = "b" if isBacksprite else ""
    _isAlter = "R" if isAlter else ""
    _isShiny = "s" if isShiny else ""

    spritePattern = "Spr {isBacksprite} {generation}{title} {pokenumber}{isAlter} {isShiny}.png"
    return spritePattern.format(isAlter= _isAlter, isShiny=_isShiny, isBacksprite=_isBacksprite, generation=generation, title=title, pokenumber=dexNumber)

def getPokemonSprites(pokeName="Bulbasaur"):
    res = requests.get('https://bulbapedia.bulbagarden.net/wiki/{pokemonName}_(Pok%C3%A9mon)'.format(pokemonName=pokeName))
    soup = BeautifulSoup(res.content, 'html.parser')

    if res.status_code == 200:
        images_set = soup.select('[alt^="Spr"]')
        for idx, image in enumerate(images_set):
            print(str(idx) + "\t| " +image["alt"])
            img = requests.get("https:"+image["src"])
            #print(img.content)

            #local testing
            fileName = str(idx)+"__"+image["alt"]
            saveImgsInFiles(fileName, img.content, True)

def saveImgsInFiles(fileName, imgBinaryData, bOverwrite=False):
    filePath = os.path.dirname(__file__) + "/../img/"
    fileFlag = 'wb' if bOverwrite else 'xb'
    with open(filePath + fileName, fileFlag) as f:
        f.write(imgBinaryData)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("scrap-poke-image")
    parser.add_argument("pokemon_name", help="Name of the Pokémon to get its sprites (Uppercase first letter)", type=str)
    args = parser.parse_args()
    getPokemonSprites(args.pokemon_name)