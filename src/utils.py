#-*- coding: utf-8 -*-

import os
import socket
import webbrowser
from urlparse import urljoin

import settings


def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def preview(url):
    webbrowser.open_new(url)


def as_url(path):
    return urljoin('http://{0}:{1}'.format(get_ip(), settings.SERVER_PORT), path)


def get_ip():
    # use baidu DNS to get the ip address
    dns = '180.76.76.76'
    try:
        return [(s.connect((dns, 53)), s.getsockname()[0], s.close())
            for s in [socket.socket(socket.AF_INET , socket.SOCK_DGRAM)]][0][1]
    except:
        return '127.0.0.1'


class cd:
    def __init__(self, new):
        self.new = os.path.expanduser(new)

    def __enter__(self):
        self.old = os.getcwd()
        os.chdir(self.new)

    def __exit__(self, etype, value, tb):
        os.chdir(self.old)
