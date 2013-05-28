#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import urllib
import urllib2
import urlparse
import cookielib
import json
import pyglet
import subprocess
import time
import codecs

verbose = False

password = "your password"
email = "hack@yourmail.com"

def login_fm(email, password):
    """Login Douban FM
"""
    login_path = "http://www.douban.com/j/app/login"
    d = urllib.urlencode({"email": email, "password": password, "app_name": "radio_desktop_mac", "version": "100"})
    cj = cookielib.CookieJar()
    # Return OpenerDirector object
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    login = opener.open(login_path, data=d)

    login_status = login.getcode()
    print "The HTTP status of the response is:", login_status
    if (login_status == 200):
        print "Login Successful!"
    # TODO: Handle wrong passwords
    return login, cj

def get_channels(cj):
    """Get all the channels
    """    
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    channels = opener.open("http://www.douban.com/j/app/radio/channels")
    channel_list = json.loads(channels.read())
    return channel_list["channels"]
    # print channel_list

def get_songs(login, cj, type="n", channel=0):
    """Get the songs from a channel.
By default type == "n", meaning that the program will request a new playlist;
b: bye
e: end
n: new
p: playing
s: skip
u: unlike
r: rated
"""
    # This is a Message object
    header_info = login.info()
    user_info = login.read()
    user_info = json.loads(user_info)
    d = urllib.urlencode({"app_name": "radio_desktop_mac", 
                          "version": "100", 
                          "user_id": user_info["user_id"], 
                          "expire": user_info["expire"],
                          "token": user_info["token"],
                          "sid": "", # What is "sid" used for?
                          "h": "",    # format: |sid1:p|sid2:s|
                          # to prevent repetitive songs
                          "channel": channel, # ? 
                          "type": "n"     # ?
                      })  

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    songs = opener.open("http://www.douban.com/j/app/radio/people", data=d)

    # This is a nested dictionary and song_list['song'] is a dictionary
    # containing all the song info
    # [x["rating_avg"] for x in song_list['song']
    song_list = json.loads(songs.read())
    return song_list['song']

def play(song):
    """Play the music and show the metadata
"""
    # Show the metadata
    if (verbose==True):
        for s in song.keys():
            print s, ":", 
            print song[s]
    else:
        print "Title:", song["title"]
        print "Artisit:", song["artist"]
        print "Album:", song["albumtitle"]
        print "Year", song["public_time"]
        print "Company:", song["company"]
        print "Length", song["length"]
    print "Playing..."
    mp3_url = song["url"]
    song_length = song["length"]
    p = subprocess.Popen(["mplayer", "-msglevel", "all=0", mp3_url])

    # At the same time, download the song:
    u = urllib2.urlopen(mp3_url)
    local_mp3 = open(song["title"] + "-" + song["artist"] + ".mp3", "w")
    local_mp3.write(u.read())
    local_mp3.close()
    # time.sleep(song_length)
    i = 0
    while(True):
        time.sleep(1)
        i += 1
        if i == song_length:
            # Kill the process when the song is finished.
            p.terminate()
            print "#" * 80
            break





cj = cookielib.CookieJar()
login, cj = login_fm(email, password)
channel_list = get_channels(cj)
print "Channels:"
for c in channel_list:
    print c['name'],
    print c['channel_id']
channel = 2
print "#" * 80
while(True):
    # Play all the songs in the current play list and when all songs are
    # played alrady, request a new playlist and continue
    song_list = get_songs(login, cj, channel = channel)
    for s in song_list:
        play(s)

