from fileFunctions import fetchSongs, fetchAllArtistSongs, createUpdatedArtistFiles
import json
import os
import glob

saveLyricsFlag = False

# def findSongFiles():
#     path = 'artists'
#     allFiles = []
#     for filename in glob.glob(os.path.join(path, '*.json')):
#         allFiles.append(filename)
#     return allFiles

if __name__ == '__main__':
    createUpdatedArtistFiles()
    #fetchSongs('data.json', saveLyricsFlag)
    # songFiles = findSongFiles()
    # for file in songFiles:
    #     
    #fetchAllArtistSongs('artists/allArtists.json')