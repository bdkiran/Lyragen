class LyricObject:
    def __init__(self, artist, title):
            self.artist = artist
            self.title = title
            self.lineNumber = []

    def addLyric(self, lyric, line):
        self.lyric = lyric
        self.lineNumber.append(line)

    def doesLyricMatch(self, lyric):
        if self.lyric == lyric:
            return True
        else:
            return False

    def addLine(self, line):
        self.lineNumber.append(line)
