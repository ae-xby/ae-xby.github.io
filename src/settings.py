#-*- coding: utf-8 -*-

import os.path

DEBUG = True

PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
root = lambda x: os.path.join(PROJECT_PATH, x)

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

SRC_PATH = root('src')
OUTPUT_PATH = root('output')
TEMPLATE_PATH = root('templates')
ASSETS_PATH = root('assets')
DOCS_PATH = root('docs')
BASE_URL = 'https://www.xiaobaiyangyixun.com'
STATIC_OUTPUT_PATH = os.path.join(OUTPUT_PATH, 'static/dist')
STATIC_PREFIX = '/static/dist'
STATIC_URL = '/static'
STATIC_SOURCE_DIRS = PROJECT_PATH

REMOTE_REPO = "git@github.com:ae-xby/ae-xby.github.io.git"
REMOTE_BRANCH = "master"

SERVER_PORT = 8888
SERVER_HOST = "0.0.0.0"

LANGUAGE = "cn"
THEME_COLOR = 'blue'
STYLE_SWITCHER_ON = True

ADDRESS = u'广州市海珠区昌岗江南坊5楼'
TEL = "020 1234 123"
EMAIL = "info@xby.com"
