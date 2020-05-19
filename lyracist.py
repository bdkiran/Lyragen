import azapi
import string
import re

def getLyricsAsArray(api, songData):
    #api = azapi.AZlyrics()
    #print(, songData['song'])
    lyrics = api.getLyrics(artist=songData['artist'], title=songData['song'], save=False)
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


if __name__ == '__main__':
    #initialize AZ api
    api = azapi.AZlyrics()

    songData = {
        'artist': 'drake',
        'song': 'blue tint'
    }
    #gets the lyrics form a-z lyrics
    lyricArray = getLyricsAsArray(api, songData)
    #cleans the lyrics data
    lyricArray = cleanLyrics(lyricArray)
    songData['lyrics'] = lyricArray
    
    print(songData)