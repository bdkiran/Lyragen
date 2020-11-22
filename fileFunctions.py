import os
import uuid
import json
from lyrics import getCleanedLyrics, getArtistSongList
from elasticsearch import Elasticsearch
from lyricObject import LyricObject

def fetchAllArtistSongs(filename):
    with open(filename) as json_file:
        artistsData = json.load(json_file)
        for artist in artistsData['artists']:
            getStoreArtistSongList(artist)

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
                if lyricArray == None:
                    continue
                objectList = createDataForStorage(songData, lyricArray)
                if esApi != None: 
                    storeSongInEs(esApi, objectList)
                    songData['fetched'] = True
                    writeToFile(filename, songsData)
                else:
                    print("lyrics: " + str(len(lyricArray)))
                    print("Objects: " + str(len(objectList)))
                    for o in objectList:
                        o.createLyricLineID()
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
    for objectTS in objectsToStore:
        res = esApi.index(index='music_lyrics', body=(objectTS.__dict__))
        print(res)

def getStoreArtistSongList(artistName):
    data = getArtistSongList(artistName, 3)
    if (data == None):
        return
    fileName = "artists/"+ artistName + ".json"
    with open(fileName, 'w') as outfile:
        json.dump(data, outfile, indent=4)


#Easy function to remove a song. Must use bool query
# def removeSongInES(artistName, songName):
#     q = {'artist': artistName, 'title': songName}
#     ES_API = Elasticsearch([{'host':'35.192.138.186','port':9200}])
#     res = ES_API.delete_by_query(index='music_lyrics', body=(q))
#     print(res)

def createUpdatedArtistFiles():
    fileName = "data.json"
    with open(fileName) as readFile:
        #Create hashmap of all artists
        # filename(artist_name) [list of songs]
        allArtistSongs = json.load(readFile)
        allArtists = []
        for song in allArtistSongs['songList']:
            if song['artist'] in allArtists:
                continue
            else:
                allArtists.append(song['artist'])
        print(len(allArtists))
        for artist in allArtists:
            artistDict = {
                "songList": []
            }
            for song in allArtistSongs['songList']:
                if song['artist'] == artist:         
                    newSong = {
                        'artist': song['artist'],
                        'title': song['title'],
                        'album': "",
                        'year': 0,
                        'fetched': True
                    }
                    artistDict["songList"].append(newSong)
                else:
                    continue
            fileName = "artists/"+ artist.lower().replace(" ", "_") + ".json"
            with open(fileName, 'w') as outfile:
                json.dump(artistDict, outfile, indent=4)

        
