# A simple static site generator

## Support Features:

- [X] Parse markdown
  - [X] Support simple markdown meta
- [X] Parse template
- [X] Generate HTML
- [X] Live Preview
- [X] Publish
- [X] Autoreload
- [ ] Publish to Github Pages
- [ ] Assets bundle
- [ ] SEO
  - [X] Meta Keywords, Description
  - [ ] Google site verification
  - [ ] Baidu site verification
  - [ ] Meta for OpenGraph
  - [ ] Meta for Facebook Applinks
  - [ ] Meta for twitter Card
  - [ ] Meta for App Banner (app-itunes-app)
- [ ] Site data collection
  - [ ] Google Analytics
  - [ ] CNZZ


## How to

- How to install

        $> pip install -r requirements.txt

- To start server run command:

        $> python src/main.py server

- To write a article run command:

        $> python src/main.py new -t "this-is-an-article"

- To see more command line support, run:

        $> python src/main.py --help

This command will create a file named `this-is-an-article.md` in
`docs/articles` directory, and start a browser to live-edit this file.
(To preview and live-edit you must start the server first.)

## Markdown meta info

- title: this will be article title
- authors: authors of this article
- date: article created time
- keywords: keywords meta info for SEO purpose
- description: description meta info about this article for SEO purpose
- draft: will not publish if article is draft.
- template: which template should use.

## Custom themes or templates

I use [jinja2](http://jinja.pocoo.org/docs/2.9/templates/) as template engine which
syntax is very simlary to django default template engine.

The templates directory structure:
```
templates
├── article.html
├── base.html
├── footer.html
├── header.html
├── index.html
├── js.html
├── list.html
└── style_switcher.html
```

- base.html: base template of all templates

To specify markdown file to use a different template, just change the markdown file
meta `template` to the template file you want.

## Publish to github Pages

- change `src/settings.py` variable `REMOTE_REPO` to you github pages repository.
- run publish command `python src/main.py pub` to publish.
