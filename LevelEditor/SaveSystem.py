import json
import os

def SaveTileTypes(tileTypes, path = "TileFiles/tileTypes.json"):
    tileTypesFile = open(path, "w")
    outputList = []

    for tileType in tileTypes:
        pass


def LoadTileTypes(path = "TileFiles/tileTypes.json"):
    pass

def SaveTilemap(tilemap, path = "TileFiles/tilemap.json"):
    tilemapFile = open(path, "w")
    outputList = []

    for i in range(len(tilemap)):
        for j in range(len(tilemap[i])):
            if(tilemap[i][j] != None):
                tile = tilemap[i][j]
                pos = tile.position
                tileDict = {
                    "Position": [pos.x, pos.y],
                    "Id": tile.tileType.id,
                }
                outputList.append(tileDict)

    jsonObject = json.dumps(outputList, indent=2)
    try:
        tilemapFile.write(jsonObject)
    except:
        print("Error occured during saving tiles")
    print("Finished saving tilemap")
    tilemapFile.close()

def LoadTilemap(path = "TileFiles/tilemap.json"):
    tilemapFile = open(path, "r")
    parsedJsonDict = json.loads(tilemapFile.read())
    tilemapFile.close()
    return parsedJsonDict

