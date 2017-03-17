#-*- coding: utf-8 -*-

import os
import shutil
import webbrowser
import datetime
from collections import namedtuple

import yaml
import mistune
from mistune_contrib import meta
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jac import CompressorExtension
from slugify import slugify

import settings
from server import start_server
from utils import makedir, preview, as_url, get_ip

markdown = mistune.Markdown()
jinja_env = Environment(
    loader=FileSystemLoader(settings.TEMPLATE_PATH),
    extensions=[CompressorExtension]
)
jinja_env.compressor_output_dir = settings.STATIC_OUTPUT_PATH
jinja_env.compressor_static_prefix = settings.STATIC_PREFIX
jinja_env.compressor_source_dirs = settings.STATIC_SOURCE_DIRS
jinja_env.filters['slugify'] = slugify
settings.SERVER_IP = get_ip()


def list_articles():
    path = os.path.join(settings.DOCS_PATH, 'articles')
    xv = map(lambda x: parse_markdown(x),
                filter(lambda x: not x.endswith('index.md'),
                    list_docs(os.path.join(settings.DOCS_PATH, 'articles'))))
    return sorted(xv,
                  key=lambda x: datetime.datetime.strptime(x['date'], settings.DATE_FORMAT),
                  reverse=True)


def get_latest_articles(n=3):
    return list_articles()[:n]


def default_settings():
    return {k: getattr(settings, k) for k in dir(settings) if k.isupper()}


def _patch_ctx(ctx):
    """value should be unicode"""
    for k, v in ctx.items():
        ctx[k] = v.decode('utf8')

    # FIXME: boolean type may be support in the future
    ctx['draft'] = True if ctx.get('draft', 'False') == 'True' else False


def list_docs(path, ext=".md"):
    """list all markdown files"""
    return [os.path.join(dirpath, fn) for dirpath, _, fns in os.walk(settings.DOCS_PATH)
            for fn in fns if fn.endswith(ext)]


def _parse_extra(ctx):
    if 'extra' in ctx:
        with open(os.path.join(settings.DOCS_PATH, ctx['extra'])) as fb:
            extra = yaml.load(fb)
            for k, func in extra.get('others', {}).items():
                if func in registers:
                    ctx[k] = registers[func]()
            ctx.update(extra)


def parse_markdown(filename):
    """Parsing markdown file"""
    relpath = os.path.relpath(filename, settings.DOCS_PATH)
    bn, _ = os.path.splitext(relpath)

    with open(filename) as fb:
        ctx, content = meta.parse(fb.read())
        ctx['content'] = markdown(content)
        ctx['url'] = '/{bn}.html'.format(bn=bn)
        ctx['output_filename'] = '{bn}.html'.format(bn=os.path.join(settings.OUTPUT_PATH, bn))
        _patch_ctx(ctx)
        _parse_extra(ctx)
        ctx.update(default_settings())
        return ctx


def render_template(ctx):
    ctx['html'] = jinja_env.get_template(ctx['template']).render(**ctx)
    return ctx


def output_html(ctx):
    html = ctx['html']
    fn = ctx['output_filename']
    makedir(os.path.dirname(fn))

    # Don't publish draft article in production
    if not ctx['DEBUG'] and ctx.get('draft', False):
        print('ignore draft article {}'.format(ctx['output_filename']))
        return

    with open(fn, 'wb') as fb:
        fb.write(html.encode('utf8'))
        print("Generated {}".format(ctx['url']))

def _publish_to_git():
    os.chdir(os.path.join(settings.OUTPUT_PATH))
    os.system('git add --all -v .')
    os.system('git commit -m "updated site on {}"'.format(
        datetime.datetime.now().strftime(settings.DATE_FORMAT)))
    os.system('git push -u --set-upstream {} {}'.format(settings.REMOTE_REPO, settings.REMOTE_BRANCH))


def publish():
    settings.DEBUG = False
    if os.path.exists(settings.STATIC_OUTPUT_PATH):
        print('clear output directory {}'.format(settings.STATIC_OUTPUT_PATH))
        shutil.rmtree(settings.STATIC_OUTPUT_PATH)
    generate()
    _publish_to_git()


def _generate(md):
    return output_html(render_template(parse_markdown(md)))


def generate():
    map(_generate, list_docs(settings.DOCS_PATH))


def _new(args):
    path = '/'.join([args.category, slugify(args.title)])
    fn = '{}.md'.format(os.path.join(settings.DOCS_PATH, path))
    fields = ('title', 'authors', 'date', 'keywords', 'description', 'template', 'draft')
    Meta = namedtuple('Meta', fields)
    meta = Meta._make([getattr(args, f) for f in fields])
    new_page(fn, meta._asdict())
    generate()
    preview(as_url(path + '.html'))


def _start_server(args):
    preview(as_url('index.html'))
    start_server(args)


def new_page(fn, meta_info):
    meta = '\n'.join('{}: {}'.format(k, v) for k, v in meta_info.items())

    if not os.path.exists(fn):
        with open(fn, 'wb') as fb:
            fb.write(meta)
            fb.write('\n\n从这里开始编辑...')
    os.system('open {}'.format(fn))


registers = {
    'get_latest_articles': get_latest_articles
}
