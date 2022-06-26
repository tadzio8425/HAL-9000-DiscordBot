import os
import hashlib
import requests
from os import path
from pathlib import Path


class get_subs:

    def __init__(self, movie_path, language):

        self.movie_path = movie_path
        self.language = language
        self.output_path = movie_path
        self.path = 0

        self.subs_found = self.search_subs()

    def get_hash(self):
        readsize = 64 * 1024
        with open(self.movie_path, 'rb') as f:
            size = os.path.getsize(self.movie_path)
            data = f.read(readsize)
            f.seek(-readsize, os.SEEK_END)
            data += f.read(readsize)
        return hashlib.md5(data).hexdigest()


    def create_url(self):
        film_hash = self.get_hash()
        url = "http://api.thesubdb.com/?action=download&hash={}&language={}".format(film_hash, self.language)
        return url


    def search_subs(self):

        try:
            url = self.create_url()
        except:
            return False
            
        header = {"user-agent": "SubDB/1.0 (SubtitleBOX/1.0; https://github.com/sameera-madushan/SubtitleBOX.git)"}
        req = requests.get(url, headers=header)
        if req.status_code == 200:
            self.download(req.content)
            return True
        else:
            return False
        


    def download(self, data):
        filename = Path(self.output_path).with_suffix('.srt')
        self.path = str(filename)
        with open(filename, 'wb') as f:
            f.write(data)
        f.close()
get_subs("\media\pi\TATAN\The Virgin Suicides (1999)\The Virgin Suicides (1999) [BluRay] [1080p] [YTS.AM].mp4", "en").search_subs()
