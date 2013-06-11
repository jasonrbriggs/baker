import postgresql

from events import add_filter, apply_filter


def get_connection(kernel):
    conf = kernel.configs['/']

    username = conf.get('database', 'username')
    password = conf.get('database', 'password')
    database = conf.get('database', 'database')

    db = postgresql.open('pq://%s:%s@localhost/%s' % (username, password, database))
    return db


def index_command(kernel, *args):
    """
    Create a search index for pages in the site.
    """
    print('Indexing site...')

    db = get_connection(kernel)

    with db.xact():
        db.prepare('delete from search')()

    ps = db.prepare('''insert into search (url, title, search_text, actual_text, last_modified)
                       values ($1, $2, to_tsvector($3), $4, $5)''')
    for page in kernel.pages.values():
        with db.xact():
            url = page.url
            if page.filename is not None and not page.filename.endswith('index.html'):
                url = page.filename
                if not url.startswith('/'):
                    url = '/' + url
            if url.endswith('/index'):
                url = url[0:-6]
            content = apply_filter('markdown', page.content)
            ps(url, page.headers['title'], page.headers['title'] + "\n" + page.content, content, page.last_modified)

    print('Complete')


def search_command(kernel, *args):
    """
    Test search for a specific keyword or set of keywords
    """
    db = get_connection(kernel)

    search = db.prepare('''select url,title
                           from search
                           where search_text @@ to_tsquery($1)
                           order by last_modified desc''')
    query = [ ]
    for word in args[0][0].split(' '):
        if word != '':
            query.append(word)

    rows = search(' & '.join(query))
    for row in rows:
        print(row[0])


def process_commands(commands):
    commands['index'] = index_command
    commands['search'] = search_command
    return commands


add_filter('commands', process_commands)