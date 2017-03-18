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

    def __init__(self, filename, content='', meta={}):
        self.meta = meta
        self.content = content
        self._filename = filename

    @property
    def filename(self):
        if self._filename is None:
            return self.build_filename()
        return self._filename

    def build_filename(self):
        return os.path.join(settings.DOCS_PATH,
                            '/'.join([self.meta.get(u'分类', 'articles'),
                                      slugify(self.meta[u'文章标题']) + '.md']))

    @property
    def output_path(self):
        bn, _ = os.path.splitext(self.relpath)
        return bn

    @property
    def relpath(self):
        return os.path.relpath(self.filename, settings.DOCS_PATH)

    @property
    def permalink(self):
        return '/{}.html'.format(self.output_path)

    @staticmethod
    def load(filename):
        if not filename.startswith(settings.DOCS_PATH):
            filename = os.path.join(settings.DOCS_PATH, filename)
        with open(filename) as fb:
            meta, content = Page.parse(fb.read())
        return Page(filename=filename, meta=meta, content=content)

    @classmethod
    def new_from_content(self, text):
        meta, content = Page.parse(text)
        return Page(filename=None, meta=meta, content=content)

    @staticmethod
    def parse(content):
        return _meta.parse(content)

    def _dump_to_file(self):
        makedir(os.path.dirname(self.filename))
        with open(self.filename, 'wb') as fb:
            fb.write(self.text)

    def save(self):
        self._dump_to_file()

    @property
    def raw_meta(self):
        return yaml.dump(self.meta, default_flow_style=False,
                         encoding="utf-8", allow_unicode=True)

    @property
    def raw_content(self):
        return self.content

    @property
    def text(self):
        return '---\n{}---\n{}'.format(self.raw_meta, self.raw_content)

    def output_html(self):
        fn = os.path.join(settings.OUTPUT_PATH, self.output_path + '.html')
        makedir(os.path.dirname(fn))
        with open(fn, 'wb') as fb:
            fb.write(self.render_html())
            print("Generated {}".format(self.permalink))


    def render_html(self):

        return jinja_env.get_template(
            self.meta[u'模板']).render(
                page=self,
                content=markdown(self.content),
                **default_context())


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
    return map(Page.load, list_source_files())


def latest_articles():
    articles = filter(lambda x: 'index' not in x,
                         list_source_files(os.path.join(settings.DOCS_PATH, 'articles')))
    pages = map(Page.load, articles)
    return sorted(pages, key=lambda p: p.meta[u'创建于'], reverse=True)


def generate_all():
    map(lambda x: x.output_html(), list_pages())
