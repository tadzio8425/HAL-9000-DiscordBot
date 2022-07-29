import requests
import urllib
from time import sleep
from random import random
from threading import Timer
import threading 
import json
import os

class RadarrAPI():


    def __init__(self):
        #Establece valores predeterminados (api_key de Radarr y la ip de la máquina que lo hostea)
        self.tracker_list = ["udp://tracker.coppersurfer.tk:6969/announce","udp://tracker.opentrackr.org:1337/announce","udp://9.rarbg.to:2710/announce","udp://9.rarbg.me:2710/announce","udp://tracker.leechers-paradise.org:6969/announce","udp://tracker.cyberia.is:6969/announce","udp://exodus.desync.com:6969/announce","http://tracker.internetwarriors.net:1337/announce","udp://explodie.org:6969/announce","udp://tracker3.itzmx.com:6961/announce","http://tracker1.itzmx.com:8080/announce","udp://tracker.tiny-vps.com:6969/announce","udp://tracker.torrent.eu.org:451/announce","udp://tracker.ds.is:6969/announce","udp://open.stealth.si:80/announce","http://open.acgnxtracker.com:80/announce","udp://retracker.lanta-net.ru:2710/announce","http://tracker4.itzmx.com:2710/announce","udp://tracker.moeking.me:6969/announce","udp://ipv4.tracker.harry.lu:80/announce"]
        
        self.host_ip = "hal9000-server.ddns.net"
        self.radarr_port = "7878"

        self.host = 'http://{ip}:{port}/api/v3/'.format(ip = self.host_ip, port = self.radarr_port)
        self.api_key = os.getenv("RADARR")
        self.api_key = 'apikey=' + self.api_key
        self.failed_search = False


    def link_shortener(self, url):
        #Acortador de links
        apiurl = "http://tinyurl.com/api-create.php?url="
        tinyurl = urllib.request.urlopen(apiurl + url).read()
        return tinyurl.decode("utf-8")


    def search_for_movie_name(self, movie_name):
        #Busca la información general de una película en base a su nombre. NO la añade NI descarga.
        movie_name = movie_name.replace(' ', '%20')
        endpoint = '/movie/lookup?term=' + movie_name
        url = self.host + endpoint + '&' + self.api_key
        r = requests.get(url)
        film_info = {}
        if r.status_code == 200:
            film_info = r.json()
        if film_info:
            return film_info[0]
        else:
            exit
            
    def add_new_movie(self, title, qualityProfileId, titleSlug, images, tmdbId, quality, year,monitored, path = "/media/pi/t4dzi01/media/movies/", addOptions = {"searchForMovie": True}):
        #En base a la infomación de una película, la AÑADE Y DESCARGA en la bibleoteca de Radarr
        #Revisa si es la primera o segunda vez que se descarga la película!
        if monitored != True:
            print("Buscando película por primera vez...")
        
            r = requests.post('http://{ip}:{port}/api/v3/movie?{api_key}'.format(ip = self.host_ip, port = self.radarr_port, api_key = self.api_key),
            json={
                'monitored':True,
                'title': title,
                'qualityProfileId': 4,
                'titleSlug': titleSlug,
                'images': images,
                'tmdbId': int(tmdbId),
                'profileId': quality,
                'year': year,
                'rootFolderPath': path,
                'addOptions' : addOptions
                
                }          
                            )
            
            film_info = {}
            if r.status_code == 200:
                film_info = r.json()
            if film_info:
                last_movie = film_info
                return last_movie
            else:
                exit
                
        else:
            print("Buscando película por segunda vez...")
            r = requests.get('http://{ip}:{port}/api/v3/movie?{api_key}'.format(ip = self.host_ip, port = self.radarr_port, api_key = self.api_key),
            json={
                'monitored':True,
                'title': title,
                'qualityProfileId': quality,
                'titleSlug': titleSlug,
                'images': images,
                'tmdbId': int(tmdbId),
                'profileId': quality,
                'year': year,
                'rootFolderPath': path,
                'addOptions' : addOptions,
                
                })
            
            film_info = {}
            if r.status_code == 200:
                film_info = r.json()
            if film_info:
                searched_film = {}
                for film in film_info:
                    if film['title'] == title:
                        searched_film = film

                #Changing quality
                searched_film['qualityProfileId'] = quality
                searched_film['profileId'] = quality
                
                searched_film_id = searched_film['id']
                #!!!!print(searched_film_id)

                searched_film_json = searched_film
                #!!!!print(searched_film_json)

                changed_film_info = self.change_movie_quality(searched_film_id, searched_film_json, quality)
                
                r = requests.post('http://{ip}:{port}/api/v3/command?{api_key}'.format(ip = self.host_ip, port = self.radarr_port, api_key = self.api_key),
                    json={
                    "name": "MoviesSearch",
                    "movieIds" : [searched_film_id]
                    })



                
            else:
                exit                 
            
                    
              
    #Función no utilizada de momento
    """def get_last_movie_torrent(self, page = 1, pageSize = 10):

        endpoint = '/history?page={}&pageSize={}'.format(page, pageSize)
        url = self.host + endpoint + '&' + self.api_key
        r = requests.get(url)
        film_info = {}
        if r.status_code == 200:
            film_info = r.json()
        if film_info:
            last_movie = film_info['records'][0]['data']
            return last_movie
        else:
            exit"""
            
            
    def get_hash_from_queue(self, page = 1, pageSize = 10):
        #Ingresa al query de las descargas desde donde obtiene el hash del torrent
        endpoint = '/queue?page={}&pageSize={}'.format(page, pageSize)
        url = self.host + endpoint + '&' + self.api_key
        r = requests.get(url)
        film_info = {}
        if r.status_code == 200:
            film_info = r.json()
        if film_info:

            try:
                last_movie = film_info["records"][0]['downloadId']
                id_number = film_info["records"][0]['id']
                size = film_info["records"][0]["size"]
                return last_movie, id_number, film_info, size

            except:
                self.get_hash_from_queue()

        else:
            exit
            
    def delete_queue_item(self, id_number):
        #Se elimina del queue la película. Se PARA COMPLETAMENTE LA DESCARGA 
        r = requests.delete('http://{ip}:{port}/api/v3/queue/{id_number}?{api_key}'.format(ip = self.host_ip, port = self.radarr_port, id_number = id_number, api_key = self.api_key))
        #!!!!print((requests.get('http://{ip}:{port}/api/v3/queue?apikey=151704df10db4125a92bc115afe9baa1')).json())

            
    def make_magnet_from_hash(self, hash):
        #Se convierte el hash en un link magnético
        magnet = "magnet:?xt=urn:btih:{}".format(hash)
        return magnet

    def set_trackers(self, magnet):
        #Se le añaden trackers al link magnetico
        magnet += "&tr="
        magnet += "&tr=".join(self.tracker_list)
        return magnet
        
            
            
    def search_and_add_movie(self ,movie_name, quality):
        #ESTA FUNCION BUSCA UNA PELÍCULA POR SU NOMBRE Y LA PONE A DESCARGAR!
        movie_info = self.search_for_movie_name(movie_name)
        result = self.add_new_movie(movie_info['title'], movie_info['qualityProfileId'], movie_info['titleSlug'], movie_info['images'], movie_info['tmdbId'],  quality, movie_info['year'], movie_info["monitored"])
        return movie_info


    def empty_queue(self):
        self.failed_search = True
        return "Not found"
   
    def set_quality(self, resolution):
        
        quality = 0

    
        if resolution == "ANY":
            quality = 1

        if resolution == "720":
            quality = 3

        if resolution == "1080":
            quality = 4

        if resolution == "4K":
            quality = 5

        return quality


    def change_movie_quality(self,movie_id ,movie_json, quality):
        print(type(movie_json))
        r = requests.put('http://{ip}:{port}/api/v3/movie/{movie_id}?{api_key}'.format(ip = self.host_ip, port = self.radarr_port, movie_id = movie_id, api_key = self.api_key), data = json.dumps(movie_json))


        print("quality changed!")

        r2 = requests.get('http://{ip}:{port}/api/v3/movie/{movie_id}?{api_key}'.format(ip = self.host_ip, port = self.radarr_port, movie_id = movie_id, api_key = self.api_key))
            
            

    def get_torrent_public(self, movie_name, local = False, past_film_id = 0, resolution = "1080"):
        

        quality = self.set_quality(resolution)
        print(quality)

        last_movie_id_file = open("last_movie_id.txt", "r")

        past_film_id = last_movie_id_file.read()


        #Funcion que debe ser utilizada para proveer torrents a un público másivo:

        #1) Se busca y se añade la película a las descargas en base a su nombre
        try:
            movie = self.search_and_add_movie(movie_name, quality)
        except:
            return None

        movie_data = movie['title'] + " " + "(" +str(movie['year']) + ")"
        movie_image = movie['images'][0]["remoteUrl"]
    

        #2) Se espera a que la película sea encontrada y añadida a la lista de descargas
        
        timer = threading.Timer(60, self.empty_queue) 
        timer.start() 

        while self.get_hash_from_queue() is None or self.get_hash_from_queue()[0] == past_film_id:
            if self.failed_search:
                self.failed_search = False
                timer.cancel()
                return None
            

        timer.cancel() 
        past_film_id = self.get_hash_from_queue()[0]
        
        last_movie_id_file = open("last_movie_id.txt", "w+")
        last_movie_id_file.write(past_film_id)

        #3) Se ingresa a la lista de descargas y se obtiene el HASH del torrent
        hash_code = self.get_hash_from_queue()

        
        
        #4) El HASH es convertido a un link magnético
        magnet = self.make_magnet_from_hash(hash_code[0])


        #5) La película es REMOVIDA de la lista de descargas una vez obtenido el link magnético
        
        self.delete_queue_item(hash_code[1])


        
        #6)Se le añaden trackers y se acorta el link
        final_magnet = self.link_shortener(self.set_trackers(magnet))


        #Se obtiene el tamaño
        size = hash_code[3]


        #7) El link magnético está listo para ser enviado al usuario
        return final_magnet, past_film_id, movie_data, movie_image, size, hash_code[0] 

    