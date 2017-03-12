import os.path
import tornado.web
import tornado.options
import tornado.ioloop
import tornado.websocket
import tornado.autoreload
from tornado.log import app_log

import autoreload
import settings
from utils import preview, as_url

ASSETS_PATH = os.path.join(settings.OUTPUT_PATH, 'assets')
STATIC_PATH = os.path.join(settings.OUTPUT_PATH, 'static')

clients = []

def reload_hook():
    from main import generate
    try:
        generate()
        map(lambda c: c.write_message('refresh'), clients)
    except Exception as e:
        print(e)

map(autoreload.watch_directory,
    [settings.DOCS_PATH, settings.ASSETS_PATH, settings.SRC_PATH, settings.TEMPLATE_PATH])
autoreload.add_reload_hook(reload_hook)

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
        (r"/(.*)$", tornado.web.StaticFileHandler, {"path": settings.OUTPUT_PATH}),
    ]

    return tornado.web.Application(urlpatterns, **config)


def start_server(options):

    tornado.options.parse_command_line()
    config = dict(
        autoreload=False,
        debug=True
    )
    app = make_app(config)
    autoreload.start()
    app.listen(settings.SERVER_PORT, address=settings.SERVER_HOST)
    app_log.info('Starting server on port {}'.format(settings.SERVER_PORT))
    preview(as_url('/index.html'))
    tornado.ioloop.IOLoop.current().start()
