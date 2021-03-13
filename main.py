from fileFunctions import fetchSongs, fetchAllArtistSongs, createUpdatedArtistFiles
from persistQL import addAllSongsFromFilesToDB, updateEsThroughDB, getValuesByArtist, getValuesByNotFetched
import json
import os
import glob

##########################################
#What does the Library need to accomplish?
##########################################
#Fetch Songs by Artist
#-On a given artist, fetch all the songs from azlyrics
#and update postgres with them
###########################################
#Fetch song lyrics
#-With the given artist, fetches all the songs listed
#in the database that have not been fetched
############################################
#Expose some basic query commands
#-All unfetched songs
#-All unfetched songs by artist
#-Show all duplicate songs in elasticsearch

saveLyricsFlag = False

if __name__ == '__main__':
    getValuesByNotFetched()
    #getValuesByArtist('Don Toliver')
    #updateEsThroughDB('Moneybagg Yo')
    #createTable()
    #addAllSongsFromFilesToDB()
    #createTable()
    #fetchAllArtistSongs('allArtists.json')
    #fetchSongs('data.json', saveLyricsFlag)
    # songFiles = findSongFiles()
    # for file in songFiles:
    #     fetchSongs(file, saveLyricsFlag)
    #fetchSongs('artists/Jay-Z.json', saveLyricsFlag)
