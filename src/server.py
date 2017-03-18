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

from git import Repo

import autoreload
import settings
from core import list_pages, Page, generate_all
from forms import PageForm


reload(sys)
sys.setdefaultencoding('utf-8')

ASSETS_PATH = os.path.join(settings.OUTPUT_PATH, 'assets')
STATIC_PATH = os.path.join(settings.OUTPUT_PATH, 'static')

s_repo = Repo(settings.PROJECT_PATH)

clients = []

def reload_hook():
    try:
        generate_all()
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
            page = Page(filename=None, meta={
                u'创建于': datetime.datetime.now().strftime(settings.DATETIME_FORMAT),
                u'分类': 'articles',
                u'文章标题': u'文章的标题',
                u'文章关键字': u'[SEO] 文章的关键字',
                u'封面': 'img/contents/default.jpg',
                u'作者': u'作者',
                u'模板': 'article.html',
                u'是否发布': True,
                u'文章描述': u'[SEO] 文章的描述'
            }, content=u'\n\n# 我是文章标题')
        else:
            page = Page.load(fp)
        self.render('templates/edit_page.html', page=page)

    def post(self, fp=None):
        content = self.get_argument('page', '')
        if not content:
            self.write('empty page. terminated!')
        else:
            meta, content = Page.parse(content.replace('\r\n', '\n'))
            filename = os.path.join(settings.DOCS_PATH, fp) if fp else None
            page = Page(filename=filename, meta=meta, content=content)
            page.save()
            reload_hook()

            # git
            print('docs/' + page.relpath)
            # s_repo.index.add('docs/' + page.relpath)
            # s_repo.index.commit(
            #     '{} article {}'.format('updated' if fp else 'added', page.relpath))
            self.redirect(page.permalink)


class DelArticleHandler(tornado.web.RequestHandler):
    def get(self, fp):
        filename = os.path.join(settings.DOCS_PATH, fp)
        if os.path.exists(filename):
            os.unlink(filename)
        s_repo.index.remove(fp)
        s_repo.index.commit("remove {}".format(fp))
        self.redirect('/a/list')


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
        (r"/a/(.+)/del", DelArticleHandler),
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
