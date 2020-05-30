import azapi
import string
import re
import json
import os
import uuid
from elasticsearch import Elasticsearch

def getLyricsAsArray(api, songData, retries):
    counter = 0
    while (counter < retries):
        print("------------------------------")
        print("Attempting to fetch: " + songData['title'])
        print("------------------------------")
        try:
            lyrics = api.getLyrics(artist=songData['artist'], title=songData['title'], save=False, search=True, sleep=10)
            return lyrics.splitlines()
        except:
            print("An exception occurred")
            counter = counter +1

    

def cleanLyrics(lyricArray):
    newLyricArray = []
    for lyricLine in lyricArray:
        #Elimate whitespace string
        if (not lyricLine or lyricLine.isspace()):
            continue
        #Eliminate [xxxx:] string
        elif (re.search(r'\[(.*?)\]', lyricLine)):
            continue
        else:
            newLyricArray.append(lyricLine)

    return newLyricArray

def storeSongInEs(esApi, songData, lyricArray):
    #count is used to create the lyric id/placement in song
    count = 0
    for lyric in lyricArray:
        songData['lyric'] = lyric
        songData['lineNumber'] = count
        #print(songData)
        count = count + 1
        res = esApi.index(index='song_lyrics', body=songData)
        print(res)


def scanFile(filename, api, esApi):
    with open(filename) as json_file:
        songsData = json.load(json_file)
        for songData in songsData['songList']:
            if (songData['fetched'] != True):
                lyricArray = getLyricsAsArray(api, songData, 3)
                #cleans the lyrics data
                lyricArray = cleanLyrics(lyricArray)
                storeSongInEs(esApi, songData, lyricArray)
                songData['fetched'] = True
                writeToFile(filename, songsData)

def writeToFile(filename, data):
    # create randomly named temporary file to avoid 
    # interference with other thread/asynchronous request
    tempfile = os.path.join(os.path.dirname(filename), str(uuid.uuid4()))
    with open(tempfile, 'w') as f:
        json.dump(data, f, indent=4)

    # rename temporary file replacing old file
    os.replace(tempfile, filename)


if __name__ == '__main__':
    ES = Elasticsearch([{'host':'localhost','port':9200}])
    api = azapi.AZlyrics()
    scanFile('data.json', api, ES)
    