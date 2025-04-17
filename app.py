from flask import Flask, render_template, abort
from flask_flatpages import FlatPages

APP = Flask(__name__)
APP.config.update({
    'FLATPAGES_EXTENSION':         '.md',
    'FLATPAGES_ROOT':              'content/posts',
    'FLATPAGES_AUTO_RELOAD':       True,
    'FLATPAGES_MARKDOWN_EXTENSIONS': [
        'fenced_code',                    # 支持 ``` 代码块
        'codehilite',                     # 代码高亮（可选）
        'markdown.extensions.extra',      # extra 里包含表格、脚注、定义列表等
        'markdown.extensions.sane_lists', # 更严格的列表解析
    ]
})

flatpages = FlatPages(APP)

@APP.route('/')
def index():
    posts = sorted(flatpages, key=lambda p: p.meta.get('Date',''), reverse=True)
    categories = sorted({ p.meta.get('Category','未分类') for p in posts })
    return render_template('index.html', posts=posts, categories=categories)

@APP.route('/category/<name>/')
def category(name):
    posts = [p for p in flatpages if p.meta.get('Category','未分类') == name]
    if not posts:
        abort(404)
    categories = sorted({ p.meta.get('Category','未分类') for p in flatpages })
    return render_template('category.html',
                           posts=posts, categories=categories, current=name)

@APP.route('/post/<path:path>/')
def post(path):
    post = flatpages.get_or_404(path)
    categories = sorted({ p.meta.get('Category','未分类') for p in flatpages })
    return render_template('post.html', post=post, categories=categories)

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=80, debug=False)
