#-*- coding: utf-8 -*-

import os
import mistune
import yaml
from mistune_contrib import yaml_meta as _meta
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jac import CompressorExtension
from slugify import slugify

import settings
from utils import makedir

markdown = mistune.Markdown()
jinja_env = Environment(
    loader=FileSystemLoader(settings.TEMPLATE_PATH),
    extensions=[CompressorExtension]
)
jinja_env.compressor_output_dir = settings.STATIC_OUTPUT_PATH
jinja_env.compressor_static_prefix = settings.STATIC_PREFIX
jinja_env.compressor_source_dirs = settings.STATIC_SOURCE_DIRS
jinja_env.filters['slugify'] = slugify


class Page(object):

    def __init__(self, filename):
        self.filename = filename
        self.meta = {}
        self.content = ''
        self.parse()
        self.bn = os.path.splitext(os.path.relpath(filename, settings.DOCS_PATH))[0]
        self.meta['url'] = '/{}.html'.format(self.bn)
        self.meta['html_file'] = os.path.join(settings.OUTPUT_PATH, self.meta['url'][1:])
        self.meta['filename'] = filename

    def parse(self):
        with open(self.filename) as fb:
            self.meta, self.content = _meta.parse(fb.read())

    def dump(self):
        with open(self.filename) as fb:
            fb.write('---\n')
            fb.write(yaml.dumps(self.meta))
            fb.write('---\n')
            fb.write(self.content)

    def output_html(self):
        fn = self.meta['html_file']
        makedir(os.path.dirname(fn))
        with open(fn, 'wb') as fb:
            fb.write(self._render().encode('utf8'))
            print("Generated {}".format(self.meta['url']))


    def _render(self):
        return jinja_env.get_template(
            self.meta['layout']).render(
                page=self, **default_context())

    @classmethod
    def render(self, filename):
        return Page(filename)._render()


def default_context():
    ctx = {k: getattr(settings, k) for k in dir(settings) if k.isupper()}
    ctx['latest_articles'] = latest_articles
    return ctx


def list_source_files(path=settings.DOCS_PATH):
    for root, dirs, files in os.walk(path):
        for fn in files:
            if fn.endswith('.md'):
                yield os.path.join(root, fn)


def list_pages():
    return map(Page, list_source_files())


def latest_articles():
    articles = filter(lambda x: 'index' not in x,
                         list_source_files(os.path.join(settings.DOCS_PATH, 'articles')))
    pages = map(Page, articles)
    return sorted(pages, key=lambda p: p.meta['created'], reverse=True)


def generate_all():
    map(lambda x: x.output_html(), list_pages())
