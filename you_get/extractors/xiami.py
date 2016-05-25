#!/usr/bin/env python
# -*- coding: utf-8 -*-

from you_get.extractor import VideoExtractor
from you_get.util.html import get_content
from you_get.util.match import match1, matchall


from xml.dom.minidom import parseString
import sys
if sys.version_info[0] == 3:
    from urllib.parse import unquote
else:
    from urlparse import unquote

def location_dec(string):
    head = int(string[0])
    string = string[1:]
    rows = head
    cols = int(len(string)/rows) + 1
    
    out = ""
    full_row = len(string) % head
    for c in range(cols):
        for r in range(rows):
            if c == (cols - 1) and r >= full_row:
                continue
            if r < full_row:
                char = string[r*cols+c]
            else:
                char = string[cols*full_row+(r-full_row)*(cols-1)+c]
            out += char
    return unquote(out).replace("^", "0")

class Xiami(VideoExtractor):
    name = "Xiami (虾米音乐)"

    song_data = None

    def prepare(self):
        if not self.vid:
            self.vid = match1(self.url, 'http://www.xiami.com/song/(\d+)', 'http://www.xiami.com/song/detail/id/(\d+)')

        xml = get_content('http://www.xiami.com/song/playlist/id/{}/object_name/default/object_id/0'.format(self.vid))
        print(xml)
        doc = parseString(xml)
        self.song_data = doc.getElementsByTagName("track")[0]

    def extract(self):
        i = self.song_data
        self.artist = i.getElementsByTagName("artist")[0].firstChild.nodeValue
        self.title = i.getElementsByTagName("songName")[0].firstChild.nodeValue
        url = location_dec(i.getElementsByTagName("location")[0].firstChild.nodeValue)
        self.stream_types.append('current')
        self.streams['current'] = {'container': 'mp3', 'video_profile': 'current', 'src' : [url], 'size': 0}


    def download_playlist(self, url, param):
        self.param = param
        if "album" in url:
            _id = match1(url, 'http://www.xiami.com/album/(\d+)')
            t = '1'
        elif "collect" in url:
            _id =match1(url, 'http://www.xiami.com/collect/(\d+)')
            t = '3'

        xml = get_content('http://www.xiami.com/song/playlist/id/{}/type/{}'.format(_id, t))
        doc = parseString(xml)
        tracks = doc.getElementsByTagName("trackList")[0]

        #ugly code TODO
        n = 0
        for t in tracks.getElementsByTagName('track'):
           if not n % 2:
               self.song_data = t
               self.download_normal()
           n += 1

site = Xiami()
