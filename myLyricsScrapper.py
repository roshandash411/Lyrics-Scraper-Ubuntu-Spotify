import dbus, requests
from bs4 import BeautifulSoup
from Tkinter import *
base_url = "https://api.genius.com"

headers = {'Authorization': 'Bearer TOKEN'}
session_bus = dbus.SessionBus()

player = session_bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')


metadata = player.Get('org.mpris.MediaPlayer2.Player', 'Metadata', dbus_interface='org.freedesktop.DBus.Properties')

print "\tSearches Lyrics From Genius"
print "\tUsing The Song Title and Song Artist"

def lyrics_from_song_api_path(song_api_path):
  song_url = base_url + song_api_path
  response = requests.get(song_url, headers=headers)
  json = response.json()
  path = json["response"]["song"]["path"]
  #gotta go regular html scraping... come on Genius
  page_url = "https://genius.com" + path
  page = requests.get(page_url)
  html = BeautifulSoup(page.text, "html.parser")
  #remove script tags that they put in the middle of the lyrics
  [h.extract() for h in html('script')]
  #at least Genius is nice and has a class called 'lyrics'!
  lyrics = html.find(class_='lyrics').get_text().encode('utf-8')
  return lyrics

previous_title = 'NULL'
print "------------------------------------------------------------------"

root = Tk()
s = Scrollbar(root)
w = Text(root, height= 60)
w.tag_configure("center", justify='center')
# w.tag_add("center", 1.0, "end")

def task(previous_title):
    metadata = player.Get('org.mpris.MediaPlayer2.Player', 'Metadata', dbus_interface='org.freedesktop.DBus.Properties')
    if metadata["xesam:title"]!=previous_title or previous_title == 'NULL':
        flag = 0
        print 'Song Title : ' + metadata["xesam:title"]
        print 'Song Artist: ' + metadata["xesam:artist"][0]
        song_title = metadata["xesam:title"]
        artist_name = metadata["xesam:artist"][0]
        if __name__ == "__main__":
          search_url = base_url + "/search"
          data = {'q': (song_title + " " + artist_name)}
          response = requests.get(search_url, data=data, headers=headers)
          json = response.json()
          song_info = None
          for hit in json["response"]["hits"]:
            # print hit["result"]["primary_artist"]["name"].upper()
            # print artist_name.upper()
            if hit["result"]["primary_artist"]["name"].upper() == artist_name.upper():
              song_info = hit
              break

          if song_info:
            song_api_path = song_info["result"]["api_path"]
            # print song_api_path
            print "Lyrics Exists. Scraping Lyrics. Please Wait ..."
            #GUI
            root.title(song_title + " -BY- " + artist_name)
            s.pack(side=RIGHT, fill=Y)
            w.pack()
            s.config(command=w.yview)
            w.config(yscrollcommand=s.set)
            w.config(state=NORMAL)
            w.config(background='#FFFF00')
            song_lyrics_001 = lyrics_from_song_api_path(song_api_path)
            w.delete(1.0, END)
            song_meta_artist_title = \
                  "Song Title : " + song_title + "\n" \
                  "Song Artist: " + artist_name 
            w.insert(1.0, song_meta_artist_title, 'center')
            w.insert(END, song_lyrics_001, 'center')
            w.config(state=DISABLED)
            # root.update_idletasks()
            # root.update()
          if not song_info:
            print "No Lyrics Found on Genius, Could Be a Remix, "
            print "Remastered, Live or a Spotify only song"
            print "Searching again with less strict parameters"
            print "High Error Expected"
            song_api_path = json["response"]["hits"][0]["result"]["api_path"]
            # print song_api_path
            print "Keep Your Fingers Crossed"
            title = json["response"]["hits"][0]["result"]["title"]
            artist_name = json["response"]["hits"][0]["result"]["primary_artist"]["name"]
            #GUI
            root.title(song_title + " -BY- " + artist_name)
            s.pack(side=RIGHT, fill=Y)
            w.pack()
            s.config(command=w.yview)
            w.config(yscrollcommand=s.set)
            w.config(state=NORMAL)
            w.config(background='#FFFF00')
            song_lyrics_001 = lyrics_from_song_api_path(song_api_path)
            w.delete(1.0, END)
            song_meta_artist_title = \
                  "Song Title : " + song_title + "\n" \
                  "Song Artist: " + artist_name 
            w.insert(1.0, song_meta_artist_title, 'center')
            w.insert(END, song_lyrics_001, 'center')
            w.config(state=DISABLED)
            # # root.update_idletasks()
            # # root.update()

        print "------------------------------------------------------------------"
        previous_title = metadata["xesam:title"]
    root.after(500, task, previous_title)
        

root.after(0, task, previous_title)
root.mainloop()
