import http.client
import sys
import socket
import re
import csv
import pickle
import os
import gzip

# MAX_CACHE_SIZE = 7800000
# THRESHOLD = 7500000
MAX_CACHE_SIZE = 4000000
THRESHOLD = 3500000
USED_CONTENT_SIZE = 0


def send_get_to_origin(origin_server, path):
    if u"\u2013" in path:
        path = re.sub(u"\u2013", "-", path)
    if "\xe5" in path:
        path = re.sub(u"\xe5", "134", path)
    if "\xe9" in path:
        path = re.sub(u"\xe9", "130", path)
    if "\xe1" in path:
        path = re.sub(u"\xe1", "160", path)
    if "ú" in path:
        path = re.sub(u"ú", "163", path)
    if "ñ" in path:
        path = re.sub(u"ñ", "164", path)
    if "ü" in path:
        path = re.sub(u"ü", "129", path)
    if "č" in path:
        path = re.sub(u"\u010d", "269", path)
    if "ć" in path:
        path = re.sub(u"ć", "263", path)
    if "\xeb" in path:
        path = re.sub(u"\xeb", "137", path)
    if "\xed" in path:
        path = re.sub(u"\xed", "214", path)
    if "\xf6" in path:
        path = re.sub(u"\xf6", "148", path)
    if "\xe6" in path:
        path = re.sub(u"\xe6", "145", path)
    if "\u0142" in path:
        path = re.sub(u"\u0142", "322", path)
    if "\xc1" in path:
        path = re.sub(u"\xc1", "193", path)
    if "\u1ebf" in path:
        path = re.sub(u"\u1ebf", "7871", path)
    if "\u0161" in path:
        path = re.sub(u"\u0161", "353", path)
    if "\u015f" in path:
        path = re.sub(u"\u015f", "351", path)
    if "\u011f" in path:
        path = re.sub(u"\u011f", "287", path)
    if "þ" in path:
        path = re.sub(u"þ", "254", path)
    if "\xf3" in path:
        path = re.sub(u"\xf3", "243", path)
    if "\xe8" in path:
        path = re.sub(u"\xe8", "43", path)
    if "\u02bc" in path:
        path = re.sub(u"\u02bc", "700", path)
    if "\xc4" in path:
        path = re.sub(u"\xc4", "196", path)
    if "\xe7" in path:
        path = re.sub(u"\xe7", "199", path)
    if "\u010c" in path:
        path = re.sub(u"\u010c", "268", path)

    origin_server.request("GET", path)
    resp = origin_server.getresponse()
    content = resp.read()
    return content

def prepopulate_cache(origin_server):

    chars = "\\/*<>?|:\""
    # cache = {}
    global USED_CONTENT_SIZE
    with open('pageviews.csv', mode='r', encoding='UTF-8') as pageviewfile:
        for line in csv.reader(pageviewfile.readlines()):
        # for line in pageviewfile:
            path = str(line[0].encode('UTF-8'))
            print(line[0])
            if USED_CONTENT_SIZE > THRESHOLD:
                break
            content = gzip.compress(
                send_get_to_origin(origin_server, "/" + line[0]))
            for c in chars:
                line[0] = line[0].replace(c, "_")

            if USED_CONTENT_SIZE + len(content) <= MAX_CACHE_SIZE:
                USED_CONTENT_SIZE += len(content)
                print(USED_CONTENT_SIZE)
                print(line[0])
                # Key = path, Value = [size, freq, content]
                with gzip.open("cache_dir/"+str(line[0]), mode='wb') as file:
                    file.write(content)
            else:
                print("Skipped")
                print(line[0])


def connect_origin(host):
    try:
        conn = http.client.HTTPConnection(host, 8080)
        return conn
    except socket.error as msg:
        sys.exit("Something when wrong with the socket connection: " + str(msg))


def main():
    args = sys.argv
    if len(args) != 2:
        sys.exit("Program is missing origin server name.")

    origin = args[1]

    origin_server = connect_origin(origin)
    if not os.path.exists("cache_dir"):
        os.makedirs("cache_dir")
    prepopulate_cache(origin_server)


main()
