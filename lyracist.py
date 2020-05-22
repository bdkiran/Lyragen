import azapi
import string
import re
import json
from elasticsearch import Elasticsearch

def getLyricsAsArray(api, songData):
    lyrics = api.getLyrics(artist=songData['artist'], title=songData['title'], save=False)
    #print(lyrics)
    return lyrics.splitlines()

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


if __name__ == '__main__':
    ES = Elasticsearch([{}])
    api = azapi.AZlyrics()
    
    with open('data.json') as json_file:
        songsData = json.load(json_file)
        for songData in songsData['songList']:
            #print(songData)
            #gets the lyrics form a-z lyrics
            lyricArray = getLyricsAsArray(api, songData)
            #cleans the lyrics data
            lyricArray = cleanLyrics(lyricArray)
            storeSongInEs(ES, songData, lyricArray)
