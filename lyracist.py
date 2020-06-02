import azapi
import string
import re
import json
import os
import uuid
from elasticsearch import Elasticsearch

saveLyricsFlag = False

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
            #Encode to find byte sequence causing issues
            lyric_utf = lyricLine.encode()
            if(lyric_utf.find(b'\xc3\xa2\xc2\x80\xc2\x99') != -1):
                #Sequence found, lets replace it with the correct chars
                cleanCharLyric = lyric_utf.replace(b'\xc3\xa2\xc2\x80\xc2\x99', b"'")
                #Remember to decode
                newLyricArray.append(cleanCharLyric.decode())
            else:
                #byte sequence was not found, no transformation needed.
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


def fetchSongsFromFile(filename, api, esApi):
    with open(filename) as json_file:
        songsData = json.load(json_file)
        for songData in songsData['songList']:
            if (songData['fetched'] != True):
                lyricArray = getLyricsAsArray(api, songData, 3)
                #cleans the lyrics data
                lyricArray = cleanLyrics(lyricArray)
                for lyric in lyricArray:
                    print(lyric)
                if esApi != None: 
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
    api = azapi.AZlyrics()
    if saveLyricsFlag: 
        ES = Elasticsearch([{'host':'localhost','port':9200}])
        fetchSongsFromFile('data.json', api, ES)
    else:
        fetchSongsFromFile('data.json', api, None)
    
    
    