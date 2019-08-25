# /usr/bin/python3
import xml.sax as sax
import requests
import json
import copy
import sys


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
            self.current_item['duration'] = int(content)


def search(name, save=False):
    base_url = "https://itunes.apple.com/search?media=podcast&country=cn&entity=podcast&term="
    handler = ItemHandler()
    r = requests.get(base_url+name)
    j = json.loads(r.text)
    if save:
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
        if save:
            with open(name+'_feed.xml', 'w') as f:
                f.write(r.text)
        sax.parseString(r.text, handler)
        return handler.items


if __name__ == '__main__':
    if len(sys.argv) > 1:
        items = search(sys.argv[1], True)
        if items:
            for i in items:
                print(i['title'])
                print('url:', i['url'])
                print('duration:', i['duration'])
