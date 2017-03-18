#-*- coding:utf-8 -*-

import sys
import datetime
import os.path
import tornado.web
import tornado.options
import tornado.ioloop
import tornado.websocket
import tornado.autoreload
from tornado.log import app_log

import autoreload
import settings
from core import list_pages, Page
from forms import PageForm


reload(sys)
sys.setdefaultencoding('utf-8')

ASSETS_PATH = os.path.join(settings.OUTPUT_PATH, 'assets')
STATIC_PATH = os.path.join(settings.OUTPUT_PATH, 'static')

clients = []

def reload_hook():
    try:
        # generate()
        # map(lambda c: c.write_message('refresh'), clients)
        pass
    except Exception as e:
        print(e)


map(autoreload.watch_directory, [
    settings.DOCS_PATH,
    settings.ASSETS_PATH,
    settings.SRC_PATH,
    settings.TEMPLATE_PATH])
autoreload.add_reload_hook(reload_hook)


class EditArticleHandler(tornado.web.RequestHandler):

    def get(self, fp=None):
        if fp is None:
            page = Page('new-filename.md', meta={
                u'创建于': datetime.datetime.now().strftime(settings.DATETIME_FORMAT),
                u'分类': 'articles',
                u'文章标题': u'文章的标题',
                u'文章关键字': u'[SEO] 文章的关键字',
                u'作者': u'作者',
                u'模板': 'article.html',
                u'文章描述': u'[SEO] 文章的描述'
            }, content=u'# 我是文章标题')
        else:
            page = Page.load(fp)
        self.render('templates/edit_page.html', page=page)

    def post(self):
        pass


class ListArticlesHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/list_pages.html', pages=list_pages())



class RefreshHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        app_log.info("WebSocket opened")
        clients.append(self)

    def on_message(self, message):
        self.write_message(u"echo: {}".format(message))

    def on_close(self):
        app_log.info("WebSocket closed")
        clients.remove(self)


def make_app(config):
    urlpatterns = [
        (r"/refresh", RefreshHandler),
        (r"/a/list", ListArticlesHandler),
        (r"/a/new", EditArticleHandler),
        (r"/a/(.+)/edit", EditArticleHandler),
        (r"/assets/(.*)$", tornado.web.StaticFileHandler,
         {"path": settings.ASSETS_PATH}
        ),
        (r"/(.*)$", tornado.web.StaticFileHandler, {"path": settings.OUTPUT_PATH}),
    ]

    return tornado.web.Application(urlpatterns, **config)


def start_server(options):

    tornado.options.parse_command_line()
    config = dict(
        autoreload=True,
        debug=True
    )
    app = make_app(config)
    autoreload.start()
    app.listen(settings.SERVER_PORT, address=settings.SERVER_HOST)
    app_log.info('Starting server on port {}'.format(settings.SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()
