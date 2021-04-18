import requests
from bs4 import BeautifulSoup
import re
import base64

import argparse # lib for parsing command parameters
import os # to get file path and be able to store images always in the img/ folder

import boto3

#SPRITE_NAME_PATTERN='Spr {isBacksprite} {generation}{title} {pokenumber}{modifiers} {isShiny}.png'
#SPRITE_NAME_REGEXP='Spr( b)?( [0-9]+)([a-z]+)( [0-9]+)([A-Z]+)?( s)?.png'
SPRITE_URL_PATTERN=re.compile('.*Spr_{optional_isBacksprite}_{generation}{title}_{dexNumber}{optional_modifiers}_{optional_gender}_{optional_isShiny}.png')
SPRITE_URL_REGEXP=re.compile('.*Spr(_b)?(_[0-9]+)([a-z]+)(_[0-9]+)([A-Z]+)?(_[mf])?(_s)?.png')

def aws_setup():
    #session = boto3.Session(profile_name='dynamoDBFullAccess')
    #db_client = session.client('dynamodb')
    boto3.setup_default_session(profile_name='dynamoDBFullAccess')
    dynamodb = boto3.resource('dynamodb')

def getSpriteSrc(dexNumber, generation, title, isBacksprite, isShiny, modifiers):
    _isBacksprite = "b" if isBacksprite else ""
    _isShiny = "s" if isShiny else ""
    #_isShiny = "_s" if isShiny else ""

    return SPRITE_URL_PATTERN.format(modifiers= modifiers, isShiny=_isShiny, isBacksprite=_isBacksprite, generation=generation, title=title, pokenumber=dexNumber)

def getPokemonSprites(pokeName="Bulbasaur"):
    pokeName = pokeName.lower().capitalize()
    urlFormat = 'https://bulbapedia.bulbagarden.net/wiki/{pokemonName}'
    res = requests.get(urlFormat.format(pokemonName=pokeName))
    soup = BeautifulSoup(res.content, 'html.parser')

    if res.status_code == 200:

        images_set = soup.select('[alt^="Spr"]')
        images_set2 = soup.find_all('img', {'src': SPRITE_URL_REGEXP})

        print("old method: {}".format(len(images_set)))
        print("new method: {}".format(len(images_set2)))

        if len(images_set2) == 0:
            print("No sprites found!")
            return

        for idx, image in enumerate(images_set2):
            print(str(idx) + "\t| " +image["alt"])
            img = requests.get("https:"+image["src"])
            #print(img.content)

            #sprite params
            spriteFullData = parseSpriteSrc(image["src"])
            spriteFullData["name"] = pokeName
            spriteFullData["sprite"] = base64.b64encode(img.content) # prepend "data:image/png;base64,"

            print("sprite params: {}".format(spriteFullData))

            #local testing
            fileName = str(idx)+"__"+image["alt"]
            saveImgsInFiles(fileName, img.content, True)

def saveImgsInFiles(fileName, imgBinaryData, bOverwrite=False):
    filePath = os.path.dirname(__file__) + "/../img/"
    fileFlag = 'wb' if bOverwrite else 'xb'
    try:
        with open(filePath + fileName, fileFlag) as f:
            f.write(imgBinaryData)
    except:
        print("Could not write on {}".format(filePath))

def parseSpriteSrc(spriteImgSrc):
    result = SPRITE_URL_REGEXP.match(spriteImgSrc)
    groups = result.groups()

    # groups[0] # (Opt.) is backsprite ("_b", None)
    # groups[1] # generation (e.g"_4")
    # groups[2] # title (e.g: "r","g","b","g","s",...)
    # groups[3] # dexNumber
    # groups[4] # (Opt.) modifiers (e.g. "R", "MX" - megaevolution in X)
    # groups[5] # (Opt.) gender ("_m","_f", None)
    # groups[6] # (Opt.) isShiny ("_s", None)

    sprite_params = {
        "isBackSprite": True if groups[0] else False,
        "generation": groups[1].strip("_"),
        "title": groups[2], # getFullTitle(generation, title)
        "dexNumber": groups[3].strip("_"),
        "modifier": groups[4],
        "gender": groups[5].strip("_") if groups[5] else groups[5], # nullCheck
        "isShiny": True if groups[6] else False,
    }
    return sprite_params


if __name__ == "__main__":
    aws_setup()
    parser = argparse.ArgumentParser("scrap-poke-image")
    parser.add_argument("pokemon_name", help="Name of the Pokémon to get its sprites", type=str)
    args = parser.parse_args()
    getPokemonSprites(args.pokemon_name)