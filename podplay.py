import podcast
import player
import sys

if len(sys.argv) <= 1:
    sys.exit(-1)
items = podcast.search(sys.argv[1])
if items:
    for i in items:
        print(i['title'])
        print('url:', i['url'])
        player.play(i['url'], i['duration'])
