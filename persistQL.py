import psycopg2
import json
import os
import glob
import traceback
from fileFunctions import fetchTupleSong

def connectToDB():
    conn = None
    try:
        conn = psycopg2.connect(
            host="192.168.1.40",
            database="nocap",
            user="postgres",
            password="postgres",
            port=5432
        )
        #Create a cursur?
        cur = conn.cursor()

        print("PostgreSQL DB Version:")
        cur.execute('SELECT version()')

        db_version = cur.fetchone()
        print(db_version)
        cur.close()
    
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')

def createTable():
    command = (
            """
            CREATE TABLE IF NOT EXISTS songs (
                song_id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                album TEXT,
                year INTEGER,
                lyrics_fetched BOOL NOT NULL
            )  
            """)
    conn = None
    try:
        conn = psycopg2.connect(
                host="192.168.1.40",
                database="nocap",
                user="postgres",
                password="postgres",
                port=5432
            )
        
        cur = conn.cursor()

        cur.execute(command)
        conn.commit()
        cur.close()
    
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')

def getValuesByArtist(artist):
    print("Finding songs by: ", artist)
    select_command = (
        """
        SELECT * FROM songs WHERE artist=%s;
        """
    )
    conn = None
    try:
        conn = psycopg2.connect(
                host="192.168.1.40",
                database="nocap",
                user="postgres",
                password="postgres",
                port=5432
            )
        
        cur = conn.cursor()
        cur.execute(select_command, (artist,))
        rows = cur.fetchall()
        for row in rows:
            print(row)
        cur.close()
    
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')

def getValuesByNotFetched():
    select_command = (
        """
        SELECT * FROM songs WHERE lyrics_fetched=FALSE;
        """
    )
    conn = None
    try:
        conn = psycopg2.connect(
                host="192.168.1.40",
                database="nocap",
                user="postgres",
                password="postgres",
                port=5432
            )
        
        cur = conn.cursor()
        cur.execute(select_command)
        print("The number of unfetched songs: ", cur.rowcount)
        rows = cur.fetchall()
        for row in rows:
            print(row)
        cur.close()
    
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')


def insert_songs(songsTuples):
    sql_command = (
        """
        INSERT INTO songs (title, artist, album, year, lyrics_fetched) 
        VALUES (%s, %s, %s, %s, %s);
        """
    )

    conn = None
    try:
        conn = psycopg2.connect(
                host="192.168.1.40",
                database="nocap",
                user="postgres",
                password="postgres",
                port=5432
        )
        
        cur = conn.cursor()
        # args_str = ','.join(cur.mogrify("(%s,%s,%s,%s,%s)", x) for x in songsTuples)
        # cur.execute("INSERT INTO songs (song_name, artist_name, album_name, year, lyrics_fetched) VALUES " + args_str) 
        for x in songsTuples:
            print("-----Inserting:")
            print(x)
            cur.execute(sql_command, x)

        print('Commiting changes.....')
        conn.commit()
        cur.close()
    
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    finally:
        if conn is not None:
            conn.close()
            print('Database Connection closed')

def update_songs(songsTuples):
    select_command = (
        """
        SELECT * FROM songs WHERE title=%s AND artist=%s;
        """
    )

    insert_command = (
        """
        INSERT INTO songs (title, artist, album, year, lyrics_fetched) 
        VALUES (%s, %s, %s, %s, %s);
        """
    )

    update_command = (
        """
        UPDATE songs SET album=%s, year=%s where song_id=%s;
        """
    )

    conn = None
    try:
        conn = psycopg2.connect(
                host="192.168.1.40",
                database="nocap",
                user="postgres",
                password="postgres",
                port=5432
        )
        
        cur = conn.cursor()
        for x in songsTuples:
            cur.execute(select_command, (x[0], x[1]))
            row = cur.fetchone()
            #Record exist, check for update.....
            if row != None:
                #Check if album and year match
                if row[3] != x[2] or row[4] != x[3]:
                    #print((x[3], x[4], row[0]))
                    cur.execute(update_command, (x[2], x[3], row[0]))
            #Record does not exist, insert into db
            else:
                cur.execute(insert_command, x)
        conn.commit()
        cur.close()
    
    except(Exception, psycopg2.DatabaseError) as error:
        tb = traceback.format_exc()
        print(tb)
    
    finally:
        if conn is not None:
            conn.close()
            print('Database Connection closed')

def fetchSongsFromDatabase(artist):
    print("Adding artist songs: ", artist)
    select_command = (
        """
        SELECT * FROM songs WHERE lyrics_fetched=FALSE AND artist=%s;
        """
    )

    update_command = (
        """
        UPDATE songs SET lyrics_fetched=TRUE WHERE song_id=%s;
        """
    )

    conn = None
    try:
        conn = psycopg2.connect(
                host="192.168.1.40",
                database="nocap",
                user="postgres",
                password="postgres",
                port=5432
        )
        
        selectCur = conn.cursor()
        selectCur.execute(select_command, (artist,))
        updateCur = conn.cursor()
        print("Number of records: ", selectCur.rowcount)
        row = selectCur.fetchone()
        while row is not None:
            successInsertInES = fetchTupleSong(row)
            if successInsertInES:
                updateCur.execute(update_command, (row[0],))
            row = selectCur.fetchone()
        
        conn.commit()
        selectCur.close()
        updateCur.close()
    
    except(Exception, psycopg2.DatabaseError) as error:
        tb = traceback.format_exc()
        print(tb)
    
    finally:
        if conn is not None:
            conn.close()
            print('Database Connection closed')

def findSongFiles(directory):
    path = "artists/{subdirectory}".format(subdirectory=directory)
    allFiles = []
    for filename in glob.glob(os.path.join(path, '*.json')):
        allFiles.append(filename)
    return allFiles

def getSongsFromFiles(songFiles):
    songTuples = []
    for filename in songFiles:
        print("----------"  + filename + "----------------")
        with open(filename) as json_file:
            songsData = json.load(json_file)
            for songData in songsData['songList']:
                songTuple = (songData['title'], songData['artist'], songData['album'], songData['year'], songData['fetched'])
                songTuples.append(songTuple)
    return songTuples

def addAllSongsFromFilesToDB():
    createTable()
    #First get all the songs that are in ES
    files = findSongFiles('goodFiles')
    tups = getSongsFromFiles(files)
    insert_songs(tups)

    #Get all the songs that are not in ES and additional metadata
    files = findSongFiles('badFiles')
    tups = getSongsFromFiles(files)
    update_songs(tups)

def updateEsThroughDB(artist):
    fetchSongsFromDatabase(artist)



    

#Postgres data structure
# Table: All Songs
# record: songName(string), artistName(string), albumName(string), year(int) lyricsFetched(bool) 