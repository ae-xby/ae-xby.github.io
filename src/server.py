import os.path
import tornado.web
import tornado.options
import tornado.ioloop
import tornado.websocket
import tornado.autoreload
from tornado.log import app_log

from settings import root, OUTPUT_PATH

ASSETS_PATH = os.path.join(OUTPUT_PATH, 'assets')
STATIC_PATH = os.path.join(OUTPUT_PATH, 'static')

clients = []

def reload_hook():
    from main import generate
    generate()
    map(lambda c: c.write_message('refresh'), clients)


tornado.autoreload.add_reload_hook(reload_hook)


class RefreshHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        app_log.info("WebSocket opened")
        clients.append(self)

    def on_message(self, message):
        self.write_message(u"echo: {}".format(message))

    def on_close(self):
        app_log.info("WebSocket closed")
        clients.remove(self)


def make_app(settings):
    urlpatterns = [
        (r"/refresh", RefreshHandler),
        (r"/(.*)$", tornado.web.StaticFileHandler, {"path": OUTPUT_PATH}),
    ]

    return tornado.web.Application(urlpatterns, **settings)


def start_server(options):

    tornado.options.parse_command_line()
    settings = dict(
        default_host=options.host,
        template_path=OUTPUT_PATH,
        debug=True
    )
    app = make_app(settings)
    app.listen(options.port)
    app_log.info('Starting server on port {}'.format(options.port))
    tornado.ioloop.IOLoop.current().start()
