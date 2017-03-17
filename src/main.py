#-*- coding: utf-8 -*-

import os
import datetime

import argparse
from app import generate, publish, _new
from utils import preview, as_url
from server import start_server
import settings


def _start_server(args):
    preview(as_url('index.html'))
    start_server(args)


def parse_command_line():
    # command line parse
    parser = argparse.ArgumentParser('XYBLOG')
    subparser = parser.add_subparsers()

    parser_gen = subparser.add_parser("gen", help="generate html")
    parser_gen.set_defaults(func=lambda args: generate())

    parser_pub = subparser.add_parser("pub", help="publish to git repo")
    parser_pub.set_defaults(func=lambda args: publish())

    parser_serve = subparser.add_parser("server", help="start http server")
    parser_serve.set_defaults(func=lambda args: _start_server(args))

    parser_new = subparser.add_parser("new", help="new article")
    parser_new.set_defaults(func=_new)
    parser_new.add_argument("-t", "--title", help="page title", required=True)
    parser_new.add_argument("-a", "--authors", help="authors", default=settings.DEFAULT_AUTHOR)
    parser_new.add_argument("--description", help="description about this page[SEO]",
                            default='...')
    parser_new.add_argument("--draft", help="draft", action='store_true',
                            default=False)
    parser_new.add_argument("--keywords", help="page keywords[SEO]",
                            default=settings.DEFAULT_KEYWORDS)
    parser_new.add_argument("-c", "--category", help="belongs to which category",
                            default=settings.DEFAULT_CATEGORY)
    parser_new.add_argument("-T", "--template", help="template to use",
                            default=settings.DEFAULT_TEMPLATE)
    parser_new.add_argument("-d", "--date", help="authors",
                            default=datetime.datetime.now().strftime(settings.DATE_FORMAT))

    return parser.parse_args()


def prepare():
    print('Initializing ...')
    _init_output()


def _init_output():
    if not os.path.exists(os.path.join(settings.OUTPUT_PATH, '.git')):
        os.system('git clone {} -b master {}'.format(
            settings.PROJECT_PATH, settings.OUTPUT_PATH))
        os.system('git remote remove origin')
        os.system('git remote add origin {}'.format(settings.REMOTE_REPO))


def main():
    prepare()
    args = parse_command_line()
    args.func(args)


if __name__ == "__main__":
    main()
