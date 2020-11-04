# Lyragen

Lyragen is a python tool to used to aquire song lyrics from AZ lyrics. After fetching the lyrics, they are then indexed in an elasticsearch database.

## Usage

After downloading the code. There is a file named data.json. To add songs, add entries to the json document with the following structure

```json
{
    "artist": "artist name",
    "title": "song name"
}
```

## Dependencies

Utilizes [azapi](https://github.com/elmoiv/azapi), a library that scrapes AZ Lyrics
