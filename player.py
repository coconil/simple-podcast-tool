import vlc
import sys


class Player:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.duration = 0
        self.media = None

    def play(self, url, wid=None, duration=-1):
        print('url:', url)
        self.media = self.instance.media_new_location(url)

        if duration < 0:
            self.media.parse()
            duration = self.media.get_duration() // 1000
        self.duration = duration
        self.player.set_media(self.media)

        if wid:
            if sys.platform.startswith('linux'):  # for Linux using the X Server
                self.player.set_xwindow(wid)
            elif sys.platform == "win32":  # for Windows
                self.player.set_hwnd(wid)
            elif sys.platform == "darwin":  # for MacOS
                self.player.set_nsobject(wid)

        self.player.play()
    def stop(self):
        if self.player.is_playing():
            self.player.stop()
    def get_duration(self):
        return self.duration

    def get_playtime(self):
        return self.player.get_time() // 1000

    def set_playtime(self, time):
        self.player.set_time(time * 1000)

    def is_playing(self):
        return self.player.is_playing()
