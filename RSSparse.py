

##
#   ISA Projekt
#   Bittorrent protokol
#   xbenom01 2015/2016
##
import sys
import xml.dom.minidom
import urllib2
import Utility

##
#   Get torrent link from RSS
#   
def getLink(rssfeed):
    xmldoc = xml.dom.minidom.parseString(rssfeed)
    items = xmldoc.getElementsByTagName("item")
    item = items[0]
    url = ""
    for childnode in item.childNodes:
        # print(childnode.nodeName)
        if(childnode.nodeName == "enclosure"):
            url = childnode.attributes["url"].value
            # print(childnode.nodeName + ": " + childnode.attributes["url"].value)
    return url

##
#   Generate movies_announce_list
#   
def genList(rssfeed):
    sys.stdout.write("Generating list\n")
    xmldoc = xml.dom.minidom.parseString(rssfeed)
    hlist = printHeader(xmldoc)

    items = xmldoc.getElementsByTagName("item")

    ilist = ""
    item = items[0]
    for item in items:
        ilist += printItem(item)
    idata = hlist + ilist
    with open("movies_announce_list.txt", 'w') as listfile:
        listfile.write(idata.encode('utf-8'))

##
#   Print list header
#   
def printHeader(doc):
    channel = doc.getElementsByTagName("channel")
    channelnodes = channel[0].childNodes

    hinfo = ""
    for node in channelnodes:
        addornot = checkHeader(node)
        if (addornot is True):
            # print(node.nodeName + ": " + node.firstChild.data)
            hinfo += node.nodeName + ": " + node.firstChild.data + "\n"
    # print("")
    hinfo += "\n"
    return hinfo

##
#   Print list item
#   
def printItem(item):
    idata = ""
    idata += "\n"
    for childnode in item.childNodes:
        addornot = checkNode(childnode)
        if(addornot is True):
            # print(childnode.nodeName + ": " + childnode.firstChild.data )
            if(childnode.firstChild is not None):
                idata += childnode.nodeName + ": " + childnode.firstChild.data + "\n"
            else:
                idata += childnode.nodeName + ": " + "\n"

    return idata

##
#   Check whether to add header
#   
def checkHeader(node):
    namelist = ["title", "link", "description"]
    for name in namelist:
        if (node.nodeName == name):
            # print("Match: " + node.nodeName + " " + name)
            return True
    return False

##
#   Check whether to add Node
#   
def checkNode(node):
    namelist = ["title", "category", "author", "link",
                "pubDate", "torrent:infoHash", "torrent:fileName"]
    for name in namelist:
        if (name == node.nodeName):
            return True
    return False

##
#   Get RSS Feed form given url
#   
def getRSSFeed(feedurl):
    sys.stdout.write("Getting RSS feed\n")
    request = urllib2.Request(feedurl)
    request.add_header('Accept-encoding', 'gzip')
    try:
        response = urllib2.urlopen(request, timeout=10)
    except:
        sys.stderr.write("Failed to download RSS\n")
        sys.exit(1)

    data = Utility.decompress(response)

    with open("movies_announce.xml", 'w') as mvfile:
        mvfile.write(data)
    return data
