import os.path

PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
root = lambda x: os.path.join(PROJECT_PATH, x)

SRC_PATH = root('src')
OUTPUT_PATH = root('output')
TEMPLATE_PATH = root('templates')
ASSETS_PATH = root('assets')
DOCS_PATH = root('docs')
BASE_URL = 'https://www.xiaobaiyangyixun.com'

LANGUAGE = "cn"
