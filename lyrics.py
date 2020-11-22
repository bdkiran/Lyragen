import azapi
import re
import pprint
import json
import time


azAPI = azapi.AZlyrics()

def getCleanedLyrics(songData, retries=3):
    lyrics_from_api = getLyricsFromAPI(songData, retries)
    if lyrics_from_api == None:
        print("Error: Unable to fetch: " + songData['title'] + " by " + songData['artist'])
        return None
    else:
        cleaned_lyrics = cleanLyrics(lyrics_from_api)
        return cleaned_lyrics

def getLyricsFromAPI(songData, retries):
    counter = 0
    while (counter < retries):
        print("------------------------------")
        print("Attempting to fetch: " + songData['title'] + " by " + songData['artist'])
        print("------------------------------")
        try:
            azAPI.artist = songData['artist']
            azAPI.title = songData['title']
            res = azAPI.getLyrics(save=False, sleep=10)
            if type(res) == int:
                raise ValueError('Unable to fetch lyrics. API error code: ' + str(res))
            return azAPI.lyrics.splitlines()
        except ValueError as error:
            print(error)
            counter = counter + 1
    
    return None
    
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

def getArtistSongList(artistName, retries=1):
    counter = 0
    while (counter < retries):
        time.sleep(10)
        try:
            print("Fetching Artist Songs: " + artistName)
            azAPI.artist = artistName
            songs = azAPI.getSongs()
            data = {}
            data['songList'] = []
            for key, songDetails in songs.items():
            #Not sure if we want mixtapes just yet....
            #or songDetails["type"] == "mixtape")
            #or songDetails["type"] == "compilation")
            #singles are listed as 'Others'
                if (songDetails["type"] == "album"): 
                    data['songList'].append({
                    "artist": artistName,
                    "title": key,
                    "album": songDetails["album"],
                    "year": songDetails["year"],
                    "fetched": False
                })
            return data
        except:
            print("An exception occurred")
            counter = counter + 1
    return None


