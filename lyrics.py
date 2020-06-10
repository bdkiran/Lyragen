import azapi
import re

azApi = azapi.AZlyrics()

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
            lyrics = azApi.getLyrics(artist=songData['artist'], title=songData['title'], save=False, search=True, sleep=10)
            return lyrics.splitlines()
        except:
            print("An exception occurred")
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

# def getArtistSongList(artistName):
#     songs = azApi.getSongs(artistName)
#     for song in songs:
#         print(song)