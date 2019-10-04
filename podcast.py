# /usr/bin/python3
import xml.sax as sax
import requests
import json
import copy
import sys
import os
import time


class ItemHandler(sax.ContentHandler):
    def __init__(self):
        self.items = []
        self.current_item = None
        self.field = None

    def startElement(self, tag, attributes):
        if tag == 'item':
            self.current_item = {}
        elif self.current_item is not None:
            if tag == 'title':
                self.field = tag
            elif tag == 'enclosure':
                self.current_item['url'] = attributes["url"]
                self.current_item['length'] = int(attributes["length"])
            elif tag == 'itunes:duration':
                self.field = tag

    def endElement(self, tag):
        if tag == 'item':
            self.items.append(copy.copy(self.current_item))
            self.current_item = None
        elif self.current_item:
            self.field = None

    def characters(self, content):
        if self.field == 'title':
            self.current_item['title'] = content
        elif self.field == 'itunes:duration':
            if content.isdigit():
                self.current_item['duration'] = int(content)
            elif content.count(':') == 1:
                t = time.strptime(content, "%M:%S")
                self.current_item['duration'] = t.tm_min * 60 + t.tm_sec
            elif content.count(':') == 2:
                t = time.strptime(content, "%H:%M:%S")
                self.current_item['duration'] = t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec


class Downloader:
    def add(self, url):
        pass

    def download(url, filename=None):
        if not filename:
            filename = url.split('/')[-1]
        else:
            filename += '.mp3'

        if os.path.exists(filename):
            return
        r = requests.get(url, stream=True)
        size = int(r.headers['content-length'])
        download_size = 0
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    download_size += len(chunk)
                    print("download: {}%".format(
                        int(download_size * 100 / size)), end='\r')
                    f.write(chunk)
            print('')


class Podcast:
    def __init__(self):
        self.podcasts = None
        self.f = None
        self.config = None

    def get_feed(self, url):
        handler = ItemHandler()
        r = requests.get(url)
        text = r.text
        sax.parseString(r.text, handler)
        return handler.items

    def get_subscribe(self):
        path_dir = os.path.expanduser('~/.config/SimplePodcast/')
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)
        self.f = open(path_dir + 'subscribe.json', 'a+')
        if self.f and self.f.tell():
            self.f.seek(0)
            self.config = json.loads(self.f.read())
            self.podcasts = self.config['podcasts']
        else:
            self.config = {'podcasts': []}
            self.podcasts = self.config['podcasts']

        return self.podcasts

    def subscribe(self, item):
        print('subs', item)
        self.podcasts.append(item)
        text = json.dumps(self.config)
        print('json: ', text)
        self.f.seek(0)
        self.f.truncate()
        self.f.write(text)
        self.f.flush()

    def unsubscribe(self):
        pass

    def search(self, name, save=False):
        base_url = "https://itunes.apple.com/search?media=podcast&country=cn&entity=podcast&term="
        handler = ItemHandler()
        r = requests.get(base_url + name)
        j = json.loads(r.text)
        if save:
            with open(name + '.json', 'w') as f:
                f.write(r.text)
        count = j['resultCount']
        if count <= 0:
            return None
        else:
            return j['results']
