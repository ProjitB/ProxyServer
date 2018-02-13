
#!/usr/bin/python

import os
import re
import socket
import sys
import threading
import time

cache = {}

def cache_check(url, conn, client_req):
    '''To Check if Requested Page is Cached'''
    TIMEOUT = 5 * 60
    global cache
    t = "time"
    c = "calls"

    orig_url = url
    url_file = ""
    for i in range(len(url)):
        if url[i] != "/":
            url_file += url[i]

    if url not in cache or time.time() - cache[orig_url][t] >= TIMEOUT:
        entry = {t: time.time(), c: 1}
        cache[orig_url] = entry
        return False

    cache[orig_url][c] += 1

    if cache[orig_url][c] < 4:
        return False

    req = client_req.split("\r\n")

    host = req[1].split(":")[1][1:]
    if len(req[1].split(":")) < 3:
        port = 80
    else:
        port = int(req[1].split(":")[2])

    print "??? Opening socket to end server at", host+":"+str(port)
    sock = socket.socket()
    sock.connect((host, port))

    print "??? Forwarding request on behalf of client to origin server at", url

    if host == "localhost" or host == "127.0.0.1":
        print "??? Origin server is located locally"

        method = req[0].split(" ")[0]

        http_pos = url.find("://")
        if http_pos != -1:
            url = url[(http_pos + 3):]

        file_pos = url.find("/")
        url = url[file_pos:]

        http_ver = req[0].split(" ")[2]

        req[0] = "%s %s %s" % (method, url, http_ver)

        if cache[orig_url][c] > 4:
            req.insert(2, "If-Modified-Since: %s" % (time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(cache[orig_url][c]))))

        new_req = ""
        for l in req:
            new_req += (l + "\r\n")

        print new_req
        sock.send(new_req)

    else:
        print "??? Origin server is located externally"

        req = client_req.split("\r\n")
        if cache[orig_url][c] > 4:
            req.insert(2, "If-Modified-Since: %s" % (time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(cache[orig_url][c]))))

        client_req = ""
        for l in req:
            client_req += (l + "\r\n")

        print client_req
        sock.send(client_req)

    print "??? Recieving response from origin server"
    response = sock.recv(1024)
    change = False
    if "304" in response.split("\r\n"):
        change = True
    print response

    print "??? Forwarding response to client"
    temp = response.split("\r\n")
    if not change:
        conn.send(response)
    else:
        temp2 = temp[0].split(" ")
        temp2[1] = "200"
        temp2[2] = "OK"
        temp2 = " ".join(temp2)
        temp[0] = temp2
        response = "\r\n".join(temp)
        conn.send(response)

    if cache[orig_url][c] > 4:
        print "??? Checking if file has been modified at origin server and sending cached file if not modified"
        if change == True:
            cache[orig_url][c] = 4
        else:
            print "??? File has not been modified; sending from cache"
            with open(url_file, 'r') as f:
                while True:
                    data = f.read(1024)
                    conn.send(data)
                    if not data:
                        break
    if cache[orig_url][c] == 4:
        print "??? Recieving fresh data from origin server and forwarding to client"
        cache[orig_url][t] == time.time()
        with open(url_file, 'wb') as f:
            while True:
                data = sock.recv(1024)
                f.write(data)
                conn.send(data)
                if not data:
                    break

    print "??? Client request fulfilled"
    return True


def request_handler(conn, addr):
    client_req = conn.recv(1024)

    req = client_req.split("\r\n")
    url = req[0].split(" ")[1]

    host = req[1].split(":")[1][1:]
    if len(req[1].split(":")) < 3:
        port = 80
    else:
        port = int(req[1].split(":")[2])

    if cache_check(url, conn, client_req):
        print "??? Closing connection to client"
        conn.close()
        print "??? Exiting thread"
        print "??? --------------------------------------------------\n\n"
        exit()
    print "??? Page hasn't been cached yet"



    print "??? Opening socket to end server at", host+":"+str(port)
    sock = socket.socket()
    sock.connect((host, port))

    print "??? Forwarding request on behalf of client to origin server at", url

    if host == "localhost" or host == "127.0.0.1":
        print "??? Origin server is located locally"

        method = req[0].split(" ")[0]

        http_pos = url.find("://")
        if http_pos != -1:
            url = url[(http_pos + 3):]

        file_pos = url.find("/")
        url = url[file_pos:]

        http_ver = req[0].split(" ")[2]

        req[0] = "%s %s %s" % (method, url, http_ver)

        new_req = ""
        for l in req:
            new_req += (l + "\r\n")

        print new_req
        sock.send(new_req)

    else:
        print "??? Origin server is located externally"

        print client_req
        sock.send(client_req)

    print "??? Recieving response from origin server"
    response = sock.recv(1024)
    print response

    print "??? Forwarding response to client"
    conn.send(response)

    print "??? Recieving data from origin server and forwarding to client"
    while True:
        data = sock.recv(1024)
        conn.send(data)
        if not data:
            break
    print "??? Client request fulfilled"

    # conn.send("<html>\n\nSending this from the proxy server to" + str(addr) + "!!!\n\n</html>\r\n")
    print "??? Closing connection to client"
    conn.close()

    print "??? Exiting thread"
    print "??? --------------------------------------------------\n\n"
    exit()

if __name__ == "__main__":
    port = 12345
    sock = socket.socket()
    sock.bind(("", port))
    print "Proxy server started on port 12345\n"
    sock.listen(5)

    while (True):
        conn, addr = sock.accept()
        print "Connection accepted", addr

        threading.Timer(0, request_handler, [conn, addr]).start()
        print ">>> Thread Created\n"
