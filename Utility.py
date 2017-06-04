

##
#   ISA Projekt
#   Bittorrent protokol
#   xbenom01 2015/2016
##
import gzip
import argparse
import sys
from StringIO import StringIO

##########################################################################


def openFile(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()
    except IOError:
        sys.stderr.write("File \"" + filename + "\" does not exist")
        sys.exit(1)
    return data

##########################################################################


def decompress(response):
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    return f.read()

##########################################################################


def parseArgs():
    args = []

    parser = argparse.ArgumentParser(
        description="Argument parser description.", add_help=False)
    parser.add_argument("-r", "--rss", help="rss feed url", dest="r")
    parser.add_argument(
        "-i", "--input-announcement", help="rss feed input", dest="i")
    parser.add_argument("-a", "--tracker-announce-url",
                        "--tracker-annonce-url", help="tracker url", dest="a")
    parser.add_argument(
        "-t", "--torrent-file", help="torrent file input", dest="t")
    parser.add_argument(
        "-h", "--help", help="show help message", action="count")
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.stderr.write("Unknown program argument, see help\n")
        sys.exit(1)
    return args
