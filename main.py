from fileFunctions import fetchSongs, fetchAllArtistSongs, scrollESDatabase
import json
import os
import glob

saveLyricsFlag = True

# def findSongFiles():
#     path = 'artists'
#     allFiles = []
#     for filename in glob.glob(os.path.join(path, '*.json')):
#         allFiles.append(filename)
#     return allFiles

if __name__ == '__main__':
    #fetchAllArtistSongs('allArtists.json')
    
    # songFiles = findSongFiles()
    # for file in songFiles:
    #     fetchSongs(file, saveLyricsFlag)
    #fetchSongs('artists/Jay-Z.json', saveLyricsFlag)
    scrollESDatabase()
