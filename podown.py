# /usr/bin/python3
import requests
import sys
import xml.sax as sax
import os
import search


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
                    int(download_size*100/size)), end='\r')
                f.write(chunk)
        print('')


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.exit(-1)
    items = search.search(sys.argv[1])
    if items:
        for i in items:
            print(i['title'])
            print('url:', i['url'])
            # / is not allowed in filename
            download(i['url'], i['title'].replace('/', '-'))
            print('')
