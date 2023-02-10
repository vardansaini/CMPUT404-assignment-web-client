#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

################################
# References
# https://stackoverflow.com/questions/4551898/separating-http-response-body-from-header-in-c AUTHOR-[j_random_hacker]
# https://www.urlencoder.io/python/ -- args in post
# Used class notes - https://eclass.srv.ualberta.ca/course/view.php?id=84313
################################

import sys
import socket
import re

# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        headers_split = data.split("\r\n")[0]
        code = headers_split.split(" ")[1]
        return int(code)

    def get_headers(self, data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    def sendall(self, data):
        self.socket.sendall(data.encode("utf-8"))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if part:
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode("utf-8")

    def check(self, path, port, args, scheme, command):
        # checks path, port and args to update as needed

        if path == "":
            path = "/"

        if port == None:
            if scheme == "http":
                port = 80
            else:
                port = 443

        if command == "POST":
            if args == None:
                args = urllib.parse.urlencode("")
            else:
                args = urllib.parse.urlencode(args)
        return path, port, args

    def request(self, command, path, host, args):
        http = " HTTP/1.1\r\n"
        connClose = "\r\nConnection:close\r\n\r\n"

        if command == "GET":
            arg = "\r\nAccept-Charset: UTF-8" + connClose
        else:
            arg = (
                "\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: "
                + str(len(args))
                + connClose
                + args
            )

        command = command + " "
        host = "Host: " + host

        request = command + path + http + host + arg
        return request

    def GET(self, url, args=None):
        parse = urllib.parse.urlparse(url)
        path = parse.path
        host = parse.hostname
        port = parse.port
        scheme = parse.scheme
        command = "GET"

        path, port, args = self.check(path, port, args, scheme, command)

        self.connect(host, int(port))

        request = self.request(command, path, host, args)

        self.sendall(request)
        response = self.recvall(self.socket)

        code = self.get_code(response)
        print(self.get_headers(response))
        body = self.get_body(response)

        self.close()
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parse = urllib.parse.urlparse(url)
        path = parse.path
        host = parse.hostname
        port = parse.port
        scheme = parse.scheme
        command = "POST"

        path, port, args = self.check(path, port, args, scheme, command)

        self.connect(host, int(port))

        request = self.request(command, path, host, args)

        self.sendall(request)
        response = self.recvall(self.socket)

        code = self.get_code(response)
        print(self.get_headers(response))
        body = self.get_body(response)

        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
