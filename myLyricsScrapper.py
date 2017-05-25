import dbus, requests
from bs4 import BeautifulSoup
from Tkinter import *
base_url = "https://api.genius.com"

headers = {'Authorization': 'Bearer TOKEN'}
session_bus = dbus.SessionBus()

player = session_bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')


metadata = player.Get('org.mpris.MediaPlayer2.Player', 'Metadata', dbus_interface='org.freedesktop.DBus.Properties')


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

while 1:
    metadata = player.Get('org.mpris.MediaPlayer2.Player', 'Metadata', dbus_interface='org.freedesktop.DBus.Properties')
    if metadata["xesam:title"]!=previous_title or previous_title == 'NULL':
        root = Tk()
        print '-------' + metadata["xesam:title"] + '-------'
        print '-------' + metadata["xesam:artist"][0] + '-------'
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
            print song_api_path
            #GUI
            s = Scrollbar(root)
            w = Text(root, height= 60)
            s.pack(side=RIGHT, fill=Y)
            w.pack()
            s.config(command=w.yview)
            w.config(yscrollcommand=s.set)
            w.insert(END, lyrics_from_song_api_path(song_api_path))
            root.mainloop()
            # root.update_idletasks()
            # root.update()
        print "------------------------------------------------------------------"
        previous_title = metadata["xesam:title"]
