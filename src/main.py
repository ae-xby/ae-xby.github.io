#-*- coding: utf-8 -*-

import os
import webbrowser
import datetime
import argparse
from collections import namedtuple

import mistune
from mistune_contrib import meta
from jinja2 import Environment, FileSystemLoader, select_autoescape
from slugify import slugify

import settings
from utils import makedir

# command line parser
parser = argparse.ArgumentParser()
markdown = mistune.Markdown()
jinja_env = Environment(
    loader=FileSystemLoader(settings.TEMPLATE_PATH)
)


def default_settings():
    return {k: getattr(settings, k) for k in dir(settings) if k.isupper()}


def _patch_ctx(ctx):
    """value should be unicode"""
    for k, v in ctx.items():
        ctx[k] = v.decode('utf8')


def list_docs(path, ext=".md"):
    """list all markdown files"""
    return [os.path.join(dirpath, fn) for dirpath, _, fns in os.walk(settings.DOCS_PATH)
            for fn in fns if fn.endswith(ext)]


def parse_markdown(filename):
    """Parsing markdown files"""
    relpath = os.path.relpath(filename, settings.DOCS_PATH)
    bn, _ = os.path.splitext(relpath)

    with open(filename) as fb:
        ctx, content = meta.parse(fb.read())
        ctx['content'] = markdown(content)
        ctx['url'] = '/{bn}.html'.format(bn=bn)
        ctx['output_filename'] = '{bn}.html'.format(bn=os.path.join(settings.OUTPUT_PATH, bn))
        _patch_ctx(ctx)
        ctx.update(default_settings())
        return ctx


def render_template(ctx):
    ctx['html'] = jinja_env.get_template(ctx['template']).render(**ctx)
    return ctx


def output_html(ctx):
    html = ctx['html']
    fn = ctx['output_filename']
    makedir(os.path.dirname(fn))

    with open(fn, 'wb') as fb:
        fb.write(html.encode('utf8'))
        print("Generated {}".format(ctx['url']))


def preview():
    from urllib import pathname2url
    uri = 'file:{}'.format(pathname2url(
        os.path.join(settings.OUTPUT_PATH, 'index.html')))
    webbrowser.open(uri)


def publish():
    generate()
    os.system('rsync -avz {}/ {}'.format(
        settings.ASSETS_PATH,
        os.path.join(settings.OUTPUT_PATH, 'assets')
    ))
    os.chdir(os.path.join(settings.OUTPUT_PATH))
    os.system('git add -u .')
    os.system('git commit -m "updated site on {}"'.format(
        datetime.datetime.now().strftime(settings.DATE_FORMAT)))
    os.system('git push')


def generate():
    map(output_html,
        map(render_template,
            map(parse_markdown, list_docs(settings.DOCS_PATH))))


def _init_output():
    if not os.path.exists(os.path.join(settings.OUTPUT_PATH, '.git')):
        os.system('git clone {} -b master {}'.format(
            settings.PROJECT_PATH, settings.OUTPUT_PATH))


# for arg parse functions
def _gen(args):
    generate()

def _pub(args):
    publish()

def _new(args):
    fn = '{}.md'.format(
        os.path.join(settings.DOCS_PATH, args.category, slugify(args.title)))
    fields = ('title', 'authors', 'date', 'keywords', 'description', 'template')
    Meta = namedtuple('Meta', fields)
    meta = Meta._make([getattr(args, f) for f in fields])
    new_page(fn, meta._asdict())

def _init_cmd_parser():
    # command line parse
    parser.add_argument("-D", "--debug",
                        help="turn on debug mode", action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    subparser = parser.add_subparsers()

    parser_gen = subparser.add_parser("gen")
    parser_gen.set_defaults(func=_gen)

    parser_pub = subparser.add_parser("pub")
    parser_pub.set_defaults(func=_pub)

    parser_new = subparser.add_parser("new")
    parser_new.set_defaults(func=_new)
    parser_new.add_argument("-t", "--title", help="page title", required=True)
    parser_new.add_argument("-a", "--authors", help="authors", default='')
    parser_new.add_argument("--description", help="description about this page[SEO]",
                            default='')
    parser_new.add_argument("--keywords", help="page keywords[SEO]", default='')
    parser_new.add_argument("-c", "--category", help="belongs to which category",
                            default='articles')
    parser_new.add_argument("-T", "--template", help="tempate to use",
                            default="article.html")
    parser_new.add_argument("-d", "--date", help="authors",
                            default=datetime.datetime.now().strftime(settings.DATE_FORMAT))

    return parser.parse_args()


def new_page(fn, meta_info):
    meta = '\n'.join('{}: {}'.format(k, v) for k, v in meta_info.items())

    if not os.path.exists(fn):
        with open(fn, 'wb') as fb:
            fb.write(meta)
            fb.write('\n\n')
    os.system('open {}'.format(fn))


def prepare():
    print('Initializing ...')
    _init_output()


def main():
    prepare()
    args = _init_cmd_parser()
    args.func(args)

if __name__ == "__main__":
    main()
