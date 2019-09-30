import vlc
import podcast
import time
import sys


def time_convert(sec):
    hour = sec // 60//60 % 24
    min = sec // 60 % 60
    sec = sec % 60
    return (hour, min, sec)


def print_play_time(time, duration):
    print('play: {}:{}:{}/{}:{}:{}'.format(time[0], time[1],
                                           time[2], duration[0], duration[1], duration[2]), end='\r')


def play(url, duration=-1):
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new_location(url)
    media.parse()
    player.set_media(media)
    if duration < 0:
        duration = media.get_duration()//1000
    player.play()
    time.sleep(3)
    while player.is_playing():
        playtime = player.get_time()//1000
        print_play_time(time_convert(playtime),
                        time_convert(duration))
        time.sleep(1)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        play(sys.argv[1])
