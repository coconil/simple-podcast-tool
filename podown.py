import requests
import json
import sys
import xml.sax as sax
import copy

base_url = "https://itunes.apple.com/search?media=podcast&country=cn&entity=podcast&term="


class ItemHandler(sax.ContentHandler):
    def __init__(self):
        self.items = []
        self.current_item = None
        self.field = None

    def startElement(self, tag, attributes):
        if tag == 'item':
            self.current_item = {}
        elif self.current_item != None:
            if tag == 'title':
                self.field = tag
            elif tag == 'enclosure':
                self.current_item['url'] = attributes["url"]
                self.current_item['length'] = int(attributes["length"])

    def endElement(self, tag):
        if tag == 'item':
            self.items.append(copy.copy(self.current_item))
            self.current_item = None
        elif self.current_item:
            self.field = None

    def characters(self, content):
        if self.field:
            self.current_item[self.field] = content


def search(name):
    handler = ItemHandler()
    r = requests.get(base_url+name)
    j = json.loads(r.text)
    with open(name+'.json', 'w') as f:
        f.write(r.text)
    count = j['resultCount']
    if count <= 0:
        print('not found.')
    else:
        select = 0
        if count > 1:
            sel_str = input('select what you want?')
            select = int(sel_str) - 1
            if select >= count or select < 0:
                return None

        feed_url = j['results'][select]['feedUrl']
        r = requests.get(feed_url)
        with open(name+'_feed.xml', 'w') as f:
            f.write(r.text)
            sax.parseString(r.text, handler)
        return handler.items


def download(url):
    filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    size=int(r.headers['content-length'])
    download_size=0
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                download_size+=len(chunk)
                print("download: {}%".format(int(download_size*100/size)),end='\r')
                f.write(chunk)
        print('\n')


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.exit(-1)
    items = search(sys.argv[1])
    if items:
        for i in items:
            print(i['title'])
            print('url:', i['url'])
            download(i['url'])
