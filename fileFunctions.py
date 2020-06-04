import os
import uuid
import json
from lyrics import getCleanedLyrics
from elasticsearch import Elasticsearch
from lyricObject import LyricObject

def fetchSongs(filename, saveFile):
    if saveFile:
        #Needs to be placed in a better place, environment variables?
        ES_API = Elasticsearch([{'host':'localhost','port':9200}])
        fetchSongsFromFile(filename, ES_API)
    else:
        fetchSongsFromFile(filename, None)

def fetchSongsFromFile(filename, esApi):
    with open(filename) as json_file:
        songsData = json.load(json_file)
        for songData in songsData['songList']:
            if (songData['fetched'] != True):
                lyricArray = getCleanedLyrics(songData)
                objectList = createDataForStorage(songData, lyricArray)
                if esApi != None: 
                    storeSongInEs(esApi, objectList)
                    songData['fetched'] = True
                    writeToFile(filename, songsData)
                else:
                    print("lyrics: " + str(len(lyricArray)))
                    print("Objects: " + str(len(objectList)))
                    for o in objectList:
                        print(o.__dict__)
                    

def writeToFile(filename, data):
    # create randomly named temporary file to avoid 
    # interference with other thread/asynchronous request
    tempfile = os.path.join(os.path.dirname(filename), str(uuid.uuid4()))
    with open(tempfile, 'w') as f:
        json.dump(data, f, indent=4)

    # rename temporary file replacing old file
    os.replace(tempfile, filename)

def createDataForStorage(songData, lyricArray):
    lyricObjectList = []
    counter = 0
    for lyric in lyricArray:
        if len(lyricObjectList) == 0:
            lo = LyricObject(songData["artist"], songData["title"])
            lo.addLyric(lyric, counter)
            lyricObjectList.append(lo)
            counter = counter +1
        else:
            lyric_found = False
            for createdLO in lyricObjectList:
                if createdLO.doesLyricMatch(lyric):
                    createdLO.addLine(counter)
                    counter = counter + 1
                    lyric_found = True
                    break
            if lyric_found == False:
                lo = LyricObject(songData["artist"], songData["title"])
                lo.addLyric(lyric, counter)
                lyricObjectList.append(lo)
                counter = counter + 1
            
    return lyricObjectList

def storeSongInEs(esApi, objectsToStore):
    #count is used to create the lyric id/placement in song
    for objectTS in objectsToStore:
        res = esApi.index(index='song_lyrics', body=(objectTS.__dict__))
        print(res)