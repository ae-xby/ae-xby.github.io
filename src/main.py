#-*- coding: utf-8 -*-

import os
import webbrowser
import mistune
from mistune_contrib import meta
from jinja2 import Environment, FileSystemLoader, select_autoescape

import settings

markdown = mistune.Markdown()
jinja_env = Environment(
    loader=FileSystemLoader(settings.TEMPLATE_PATH),
)


def default_settings():
    return {k: getattr(settings, k) for k in dir(settings) if k.isupper()}


def _patch_ctx(ctx):
    """value should be unicode"""
    for k, v in ctx.items():
        ctx[k] = v.decode('utf8')


def list_docs(path, ext=".md"):
    """list all markdown files"""
    return map(lambda x: os.path.join(path, x),
               filter(lambda x: x.endswith(ext), os.listdir(path)))


def parse_markdown(filename):
    """Parsing markdown files"""
    basename = os.path.basename(filename)
    bn, _ = os.path.splitext(basename)

    with open(filename) as fb:
        ctx, content = meta.parse(fb.read())
        ctx.update(default_settings())
        ctx['content'] = markdown(content)
        ctx['url'] = '/{bn}.html'.format(bn=bn)
        ctx['output_filename'] = '{bn}.html'.format(bn=bn)
        _patch_ctx(ctx)
        return ctx


def render_template(ctx):
    ctx['html'] = jinja_env.get_template(ctx['template']).render(**ctx)
    return ctx


def generate(ctx):
    html = ctx['html']
    fn = os.path.join(settings.OUTPUT_PATH, ctx['output_filename'])

    if not os.path.exists(settings.OUTPUT_PATH):
        os.makedirs(settings.OUTPUT_PATH)

    with open(fn, 'wb') as fb:
        fb.write(html.encode('utf8'))
        print("Generated {}".format(ctx['url']))


def preview(path):
    from urllib import pathname2url

    uri = 'file:{}'.format(pathname2url(os.path.join(path, 'index.html')))
    webbrowser.open(uri)


def main():

    map(generate,
        map(render_template,
            map(parse_markdown, list_docs(settings.DOCS_PATH))))
    preview(settings.OUTPUT_PATH)


if __name__ == "__main__":
    main()
