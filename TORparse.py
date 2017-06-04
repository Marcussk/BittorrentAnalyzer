

##
#   ISA Projekt
#   Bittorrent protokol
#   xbenom01 2015/2016
##
import bencode
import hashlib
import requests
import sys
import Utility

##
#   GET infohash key from torrent data
#   
def getInfoHash(torrentdata):
    infodic = torrentdata["info"]
    encinfo = bencode.bencode(infodic)
    sha1 = hashlib.sha1(encinfo).digest()
    return sha1


##
#   GET Announce key from torrent data
#   
def getAnnounce(torrdata):
    trackurl = torrdata["announce"]
    return trackurl


##
#   Open torrent from given path
#   
def openTorrent(location):
    sys.stdout.write("Opening torrent\n")
    torrdata = Utility.openFile(location)
    try:
        decdata = bencode.bdecode(torrdata)
    except:
        sys.stderr.write("Cant decode torrent data from location: " + location) + "\n"
        sys.exit(1)
    # print(decdata)
    return decdata

##
#   Get torrent from given url
#   
def getTorrent(url):
    sys.stdout.write("Getting torrent\n")
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept-Charset': 'utf-8',
           'Accept-Encoding': 'gzip',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    try:
        request = requests.get(url, headers=hdr, timeout=10)
    except:
        sys.stderr.write("Failed to download torrent file\n")
        sys.exit(1)
    try:
        data = bencode.bdecode(request.content)
    except:
        sys.stderr.write("Can not decode torrent data from location: " + url + "\n")
        sys.exit(1)
    return data
