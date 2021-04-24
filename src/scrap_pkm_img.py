import requests
from bs4 import BeautifulSoup
import re
import base64 # convert img binary data to b64
import time # get timestamp
from decimal import Decimal # convert timestamp to decimal

import argparse # lib for parsing command parameters
import os # to get file path and be able to store images always in the img/ folder

import boto3
from boto3.dynamodb.conditions import Key, Attr # Querying and scanning

#SPRITE_NAME_PATTERN='Spr {isBacksprite} {generation}{title} {pokenumber}{modifiers} {isShiny}.png'
#SPRITE_NAME_REGEXP='Spr( b)?( [0-9]+)([a-z]+)( [0-9]+)([A-Z]+)?( s)?.png'
SPRITE_URL_PREFIX='//cdn.bulbagarden.net/upload/9/9d/'
SPRITE_URL_PATTERN='Spr{isBacksprite}_{generation}{title}_{dexNumber}{modifiers}{gender}{isShiny}.png'
SPRITE_URL_REGEXP=re.compile('.*Spr(_b)?(_[0-9]+)([a-z]+)(_[0-9]+)([A-Z]+)?(_[mf])?(_s)?.png')

IMAGE_DATA_PREFIX='data:image/png;base64,'

###
# AWS TABLE SETUP AND METHODS
###

boto3.setup_default_session(profile_name='dynamoDBFullAccess')

def setupAwsTable():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('PokeSprites')
    return table

def writeSpriteToDB(spriteData):
    table = setupAwsTable()
    table.put_item(Item=spriteData)

def getSpriteFromDB(spriteData):
    table = setupAwsTable()
    response = table.get_item(
        Key={
            'name': spriteData["name"],
            'index': spriteData["index"]
        }
    )
    item = response['Item']
    return item

def writeSpriteBatchToDB(spriteDataArray):
    table = setupAwsTable()
    with table.batch_writer() as batch:
        for i in range(len(spriteDataArray)):
            batch.put_item(Item=spriteDataArray[i])

def getPokemonSpritesFromDB(pokeName):
    table = setupAwsTable()
    lastEvaluatedKey = -1
    retrievedSprites = []
    while lastEvaluatedKey != None:
        if lastEvaluatedKey == -1 :
            response = table.query(
                KeyConditionExpression=Key('name').eq(pokeName)
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('name').eq(pokeName),
                ExclusiveStartKey=lastEvaluatedKey
            )
        retrievedSprites += response['Items']
        lastEvaluatedKey = response['LastEvaluatedKey'] if 'LastEvaluatedKey' in response.keys() else None
    return retrievedSprites

###
# POKE SPRITES SCRAPPING
###

def getSpriteSrc(isBackSprite, generation, title, dexNumber, modifiers, gender, isShiny):
    sBacksprite = "_b" if isBackSprite else ""
    sGender = "_"+gender if gender else ""
    sShiny = "_s" if isShiny else ""

    return SPRITE_URL_PATTERN.format(isBacksprite=sBacksprite, generation=generation, title=title, dexNumber=dexNumber, modifiers= modifiers, gender=sGender, isShiny=sShiny)

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

        spriteDataArray = []

        for idx, imageTag in enumerate(images_set2):
            print(str(idx) + "\t| " +imageTag["alt"])
            imageRequest = requests.get("https:"+imageTag["src"])
            # print(img.content)

            #sprite params
            spriteFullData = getSpriteFullData(pokeName, idx, imageTag["src"], imageRequest.content)
            print("sprite params: {}".format(spriteFullData))

            # add to total
            spriteDataArray.append(spriteFullData)

            # local testing - save images locally
            fileName = str(idx)+"__"+imageTag["alt"]
            saveImgsInFiles(fileName, imageRequest.content, True)

        # print("This is the sprite data: {}".format(spriteDataArray))
        return spriteDataArray

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

def getSpriteFullData(pokeName, index, imageSrc, imageBinaryData):
    spriteFullData = parseSpriteSrc(imageSrc)
    spriteFullData["name"] = pokeName # partition key
    spriteFullData["index"] = index # used a sort key, used to create a unique id since name (partition key) is not unique
    spriteFullData["sprite"] = base64.b64encode(imageBinaryData) # prepend "data:image/png;base64,"
    spriteFullData["timestamp"] = int(time.time()) # DynamoDB does not accept floats
    return spriteFullData

###
# MAIN
###

if __name__ == "__main__":
    parser = argparse.ArgumentParser("scrap-poke-image")
    parser.add_argument("pokemon_name", help="Name of the Pokémon to get its sprites", type=str)
    args = parser.parse_args()
    writeSprite = False
    if writeSprite:
        spriteData = getPokemonSprites(args.pokemon_name)
        #print("sprite data: {}".format(spriteData))
        writeSpriteBatchToDB(spriteData)
    else:
        #res = getSpriteFromDB({'name': 'Charizard', 'index': 10})
        #res['sprite']=IMAGE_DATA_PREFIX+res['sprite'].__str__().decode('ascii')
        res = getPokemonSpritesFromDB(args.pokemon_name)
        print(res)