import os

def muzik_cal(song_name):
    # Önce çalan bir şey varsa sustur
    os.system("pkill -9 mpv > /dev/null 2>&1")
    # Yeni müziği başlat
    os.system(f'mpv --no-video "ytdl://ytsearch:{song_name}" &')

def her_seyi_sustur():
    os.system("pkill -9 mpv > /dev/null 2>&1")
    os.system("pkill -9 mpg123 > /dev/null 2>&1")
