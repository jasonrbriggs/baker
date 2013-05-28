import os
import sys

from events import add_filter, apply_filter, do_action

default_ini = '''
[site]
domain=<your domain name>
title=<your site title>

[control]
plugins=menu

[templates]
index=index.html
default=page.html
head=head.html
foot=foot.html

[blog]
paths = /blog

[tags]
index_title=Tags
title=Tag: %%s
5=tag5
10=tag10
15=tag15
20=tag20
'''

default_head = '''
<head eid="head">
<title eid="title"></title>
<meta aid="generator" name="generator" content="" />
<meta content="text/html;charset=utf-8" http-equiv="Content-Type" />
<meta content="utf-8" http-equiv="encoding" />
<link rel="stylesheet" href="/theme/main.v1.css" type="text/css" media="screen"></link>
</head>
'''

default_foot = '''
<div id="footer">

</div>
'''

default_page = '''
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head eid="head"></head>
<body>
<div eid="content">

</div>

<div eid="foot">

</div>
</body>
</html>
'''

default_post = '''
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head eid="head"></head>
<body>
    <div id="postcontainer">
        <div rid="posts">
            <div eid="content">

            </div>
            <div class="metacontainer">
                <span eid="posted-on"></span><span> | </span><a aid="permalink" eid="permalink" href=""></a><br />
                <div class="tagcontainer"><span eid="tags"></span><span rid="taglinks"><a eid="taglink" aid="taglink" href=""></a></span></div>
            </div>
        </div>
        <div id="pagelinkcontainer">
            <a eid="prevpage" aid="prevpage" href=""></a>
            <span eid="pagelinksep"></span>
            <a eid="nextpage" aid="nextpage" href=""></a>
        </div>
    </div>

    <div eid="foot"></div>
</body>
</html>
'''

default_tags = '''
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head eid="head"></head>
<body>
    <div id="postcontainer">
        <ul class="tags">
            <li rid="tags">
                <a eid="tag" aid="tag" href="" class=""></a>
            </li>
        </ul>
    </div>

    <div eid="foot"></div>
</body>
</html>
'''

default_tag = '''
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head eid="head"></head>
<body>
    <div id="postcontainer">
        <h2 eid="tag"></h2>

        <div rid="posts">
            <div eid="content">

            </div>
            <div class="metacontainer">
                <span eid="posted-on"></span><span> | </span><a aid="permalink" eid="permalink" href=""></a><br />
                <div class="tagcontainer"><span eid="tags"></span><span rid="taglinks"><a eid="taglink" aid="taglink" href=""></a></span></div>
            </div>
        </div>
        <div id="pagelinkcontainer">
            <a eid="prevpage" aid="prevpage" href=""></a>
            <span eid="pagelinksep"></span>
            <a eid="nextpage" aid="nextpage" href=""></a>
        </div>
    </div>

    <div eid="foot"></div>
</body>
</html>
'''

default_text = '''
title: [a page title]
template: index.html
tags: testtag

A Page Title
============

Your content goes here. Enter using [Markdown](http://daringfireball.net/projects/markdown/) syntax.

'''

def write_file(name, content):
    with open(name, 'w') as f:
        f.write(content)

def generate_files(path):
    write_file(os.path.join(path, 'site.ini'), default_ini)
    write_file(os.path.join(path, 'theme', 'main.v1.css'), '')
    write_file(os.path.join(path, 'theme', 'head.html'), default_head)
    write_file(os.path.join(path, 'theme', 'foot.html'), default_foot)
    write_file(os.path.join(path, 'theme', 'index.html'), default_page)
    write_file(os.path.join(path, 'theme', 'page.html'), default_page)
    write_file(os.path.join(path, 'theme', 'post.html'), default_post)
    write_file(os.path.join(path, 'theme', 'tags.html'), default_tags)
    write_file(os.path.join(path, 'theme', 'tag.html'), default_tag)
    write_file(os.path.join(path, 'index.text'), default_text)

def newsite(kernel, *args):
    if len(args) <= 0 or len(args[0]) <= 0:
        print('A path to generate the new site is required')
        sys.exit(1)
    elif os.path.exists(args[0][0]):
        print('Path "%s" already exists' % args[0][0])
        sys.exit(1)

    path = args[0][0]
    os.makedirs(path)
    os.makedirs(os.path.join(path, 'theme'))
    os.makedirs(os.path.join(path, 'tags'))
    os.makedirs(os.path.join(path, 'resources'))

    generate_files(path)


def process_commands(commands):
    commands['new'] = newsite
    return commands

add_filter('commands', process_commands)