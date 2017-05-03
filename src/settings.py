#-*- coding: utf-8 -*-

import os.path

DEBUG = True

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root = lambda x: os.path.join(PROJECT_PATH, x)

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

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

SERVER_PORT = 8881
SERVER_HOST = "0.0.0.0"

LANGUAGE = "cn"
THEME_COLOR = 'blue'
STYLE_SWITCHER_ON = True

ADDRESS = u'广州市海珠区昌岗东路252号江南坊5楼元空间520室'
ROUTE_GUIDE = 'http://j.map.baidu.com/nZN0B'
TEL = "020-84108722"
EMAIL = "info@xby.com"
WEIXIN_GZH_QR = "img/team/qrcode.jpeg"
WEIXIN_GZH = u"晓白杨传媒艺训"
LOGO_URL = 'img/team/logo.png'

DEFAULT_AUTHOR = '刘老师'
DEFAULT_KEYWORDS = "晓白杨精品艺训班"
DEFAULT_TEMPLATE = 'article.html'
DEFAULT_CATEGORY = 'articles'

CNZZ = '1261484799'
