class LyricObject:
    def __init__(self, artist, title):
            self.artist = artist
            self.title = title
            self.lineNumber = []

    def addLyric(self, lyric, line):
        self.lyric = lyric
        self.lineNumber.append(line)

    def doesLyricMatch(self, lyric):
        if self.lyric.lower() == lyric.lower():
            return True
        else:
            return False

    def addLine(self, line):
        self.lineNumber.append(line)
    
    def createLyricLineID(self):
        #Lyric line ID should look like?:
        # artist@name#number.number
        lineString = ""
        for lineNum in self.lineNumber:
            if lineString == "":
                lineString = str(lineNum)
            else:
                lineString = "{existingLineString}.{newLineNum}".format(existingLineString=lineString, newLineNum=lineNum)
        
        self.lineID = "{artist}@{songTitle}#{lineStringNums}".format(artist=self.artist, songTitle=self.title, lineStringNums=lineString)
        
