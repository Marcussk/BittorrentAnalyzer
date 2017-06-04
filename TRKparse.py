

##
#   ISA Projekt
#   Bittorrent protokol
#   xbenom01 2015/2016
##
import socket
import sys
import re
import struct
import string
import TORparse
import bencode
import random
###urlib?
import urllib

##
#   Hlavna funkcia pre ziskanie zoznamu trackerov
#   parameters: torrent data, announce parameter programu
def getPeerList(torrdata, announce):
    peerdata = ""
    trackerlist = []
    # print("Getting peerlist")

    if (announce == ""):
        for url in torrdata["announce-list"]:
            trackerlist.append(url[0])
        if not trackerlist:
            announce = TORparse.getAnnounce(torrdata)
            trackerlist.append(announce)
    else:
        trackerlist.append(announce)

    random.shuffle(trackerlist)

    # print("Trackerlist: ")
    # print(trackerlist)

    for tracker in trackerlist:
        peerdata += trackConnection(tracker, torrdata)
        # print("Peers:\n" + peerdata)
    filename = TORparse.getInfoHash(torrdata).encode("hex")
    writePeerList(filename, peerdata)

##
#   Get all parameters from url
#   parameters: tracker url
#   returns port, host, path and optional params, port
##
def parseUrl(url):
    port = 80
    path = ""
    params = None
    if (url[0:3] == "udp"):
        protocol = "udp"
        address = url[6:]
    elif (url[0:4] == "http"):
        protocol = "http"
        address = url[7:]
    else:
        sys.stderr.write("Error: Unrecognized protocol in: \"" + url + "\"\n")
        return None, None, None, None

    # print("Address: " + address)
    domain = address.split('/')

    #
    #   PATH + REMAINDER
    #   
    if(len(domain) > 1):
        additions = domain[1].split('?')
        path = additions[0]
        if (len(additions) > 1):
            params = additions[1]

    name = domain[0]

    #
    #   HOST + PORT
    #   
    hostinfo = name.split(':')
    host = hostinfo[0]
    if (len(hostinfo) > 1):
        port = hostinfo[1]

    # print("Host: " + host)
    # print("Port: " + str(port))
    # print("Path: " + path)    
    return protocol, host, port, path, params


##
#   Returns query according to Bittorrent Tracker protocol
#   parameters: torrent data
#   returns: request
##
def getQuery(torrdata):
    # print(torrdata)
    info_hash = urllib.quote_plus(TORparse.getInfoHash(torrdata))

    # pid = '-MC2250-001498523664'
    randomstr = ''.join(random.choice(string.lowercase) for i in range(20))
    # print(pid)
    # print(randomstr)
    pid = randomstr
    peer_id = urllib.quote_plus(pid)
    request = "info_hash=" + info_hash
    request += "&peer_id=" + peer_id
    request += "&event=started"
    request += "&port=6881"
    request += "&uploaded=0"
    request += "&downloaded=0"
    request += "&left=1"

    request += "&numwant=1000"
    request += "&compact=1"

    return request

##
#   Returns GET message composed from all parts
#   parameters: data returned by parseUrl
#   returns GET request
def getMessage(path, host, query, params):
    if (params is not None):
        params += "&"
        query = (params + query)

    message = "GET /" + path + "?"
    message += query + " HTTP/1.0\r\n"

    message += "User-Agent: Python\r\n"
    message += "Host: " + host + "\r\n"
    message += "Connection: close\r\n"
    #message += "Content-Type: text/plain\r\n"
    message += "\r\n"
    # print(message)
    return message


##
#   Prepare for connection to tracker
#   parameters: tracker url, torrent data
#   returns peerlist
def trackConnection(url, torrdata):
    query = getQuery(torrdata)
    protocol, address, port, path, params = parseUrl(url)
    message = getMessage(path, address, query, params)

    # print("Url: " + url)
    # print("Query: " + query)
    # print("Protocol: " + protocol)
    # print("Address: " + address)
    # print("Port: " + str(port))
    # print("Path: " + path)
    # print("Message: " + message)

    if (protocol is None):
        return ""

    if (protocol == "udp"):
        data = udpretrieve(address, port, message, url)

    if (protocol == "http"):
        data = tcpretrieve(address, port, message, url)

    # print("Response: " + response)
    return data


##
#   Udp connection to tracker
def udpretrieve(address, port, message, url):
    return ""

##
#   Tcp connection to tracker
#   parameters: address and port of tracker, message for tracker and its url
#   returns peerlist
def tcpretrieve(address, port, message, url):
    print("Retrieving data from: " + url)
    # print("Message: " + message)
    line = 0
    response = ""
    contentLength = 1024
    #
    #   SOCKET
    # 
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as ex:
        sys.stderr.write("Socket.socket: " + str(ex.errno) + " " + ex.strerror)
        return ""

    sock.settimeout(10)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #
    # CONNECT
    # 
    try:
        sock.connect((address, int(port)))
    except socket.error, msg:
        sys.stderr.write("Socket.connect: " + str(msg) + "\n")
        return ""
    except socket.gaierror, msg:
        sys.stderr.write("Socket.connect: " + str(msg) + "\n")
        return ""
    except socket.timeout, msg:
        sys.stderr.write("Socket.connect: " + str(msg) + "\n")
        return ""
    except:
        sys.stderr.write("Exception during connect\n")
        return ""
    #
    #   SEND
    #   
    try:
        sock.sendall(message)
    except IOError:
        sys.stderr.write("Send failed\n")
        return ""
    except:
        sys.stderr.write("Exception during send\n")
        return ""
    #   
    #   RECEIVE HEADER
    #   
    header = ""
    while 1:
        try:
            data = sock.recv(1)
            # print(str(data))
            # sys.stdout.write(str(data))
            if not data:
                break
            header += data
            if ((header[-2:] == '\r\n') & (line == 0)):
                print(header[:-2])
                line += 1
            if header[-4:] == '\r\n\r\n':
                contentLength = getContentLength(header)
                break
        except socket.error, msg:
            sys.stderr.write("Socket.recv header: " + str(msg) + "\n")
            return ""
        except socket.timeout, msg:
            sys.stderr.write("Socket.recv header: " + str(msg) + "\n")
            return ""
        except:
            sys.stderr.write("Receive header exception\n")
            return ""

    #
    #   RECEIVE BODY
    #   
    # print("Content-Length: " + contentLength)

        # print("No message body received")
    msgdata = ""
    body = ""
    while 1:
        msgdata = sock.recv(int(contentLength))
        if not msgdata:
            break
        body += msgdata
    response = body
    #
    #   PARSE RESPONSE
    #   
    peers = parseResponse(response)

    sock.close()
    return peers

##
#   getContentLength
#   parameters: header returned by tracker
#   return: length of message body
def getContentLength(msg_header):
    length = 2048
    regex = r'Content-Length: ([0-9]*)'
    content = re.search(regex, msg_header)
    if (content is not None):
        length = content.group(1)
    return length

##
#   Vrati zoznam peerov z odpvoede trackeru
#   parameters: peers polozka trackeru
#   returns: zoznam peerov a cih pocet
def unpack(peers):
    # print("unpacked:\n")
    number = 0
    pdata = ""
    i = 0
    length = len(peers)
    while (i < length):
        port = struct.unpack_from('!H', peers, offset=i + 4)[0]
        ip = socket.inet_ntoa(peers[i:i + 4])
        # print(ip + ":" + str(port))
        pdata += ip + ":" + str(port) + "\n"
        i += 6
        number += 1
    return pdata, number

##
#   Vrati zoznam peerov z odpvoede trackeru
#   parameters: peers polozka trackeru
#   returns: zoznam peerov a ich pocet
def getData(peers):
    # print("Data: \n")
    number = 0
    pdata = ""
    for peer in peers:
        pdata += str(peer["ip"]) + ":" + str(peer["port"]) + "\n"
        number += 1
    return pdata, number

##
#   Spracovanie odpovedi trackeru a parsovanie peer zoznamu
#   parameters: odpoved trackru
#   returns peerlist
def parseResponse(contents):
    data = ""
    # print("Contents: " + contents)
    
    #
    #   DECODE
    #   
    try:
        t = bencode.bdecode(contents)
    except:
        sys.stderr.write("Can not decode data from tracker\n")
        return ""
    # print(t)
    
    # 
    #   GET PEERS
    #   
    if("peers") in t:
        peers = t["peers"]
    elif ("failure reason") in t:
        print(t["failure reason"])
        return ""
    else:
        print("Malformed data received from tracker")
        return ""

    #
    #   PARSE PEERS
    #   
    if isinstance(peers, list):
        # print("list")
        data, number = getData(peers)
    else:
        # print("else")
        data, number = unpack(peers)
    sys.stdout.write("Received " + str(number) + " peers\n")
    return data

##
#   Zapis peerlistu do suboru
#   parameters: infohash z torrentu, peerlist
def writePeerList(info_hash, data):
    filename = info_hash + ".peerlist"
    sys.stdout.write("Writing into: " + filename + "\n")
    with open(filename, 'w') as peerfile:
        peerfile.write(data)
