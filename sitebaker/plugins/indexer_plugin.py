import datetime
import postgresql

from baker import add_filter, add_action

def get_connection(kernel):
    conf = kernel.configs['/']

    username = conf.get('database', 'username')
    password = conf.get('database', 'password')
    database = conf.get('database', 'database')

    db = postgresql.open('pq://%s:%s@localhost/%s' % (username, password, database))
    return db

def index_command(kernel, *args):
    print('Indexing site...')

    db = get_connection(kernel)

    for page in kernel.pages.values():
        print('  processing %s' % page.url)
        #print('     content %s' % page.content)

        ps = db.prepare('select id, last_modified from search_pages where url = $1')
        rows = ps(page.url)

        if len(rows) == 0:
            ps = db.prepare('insert into search_pages (url, last_modified) values ($1, $2)')
            ps(page.url, datetime.datetime.fromtimestamp(page.last_modified))
        else:
            print(rows[0][1])
            print('>>>>>>>>> last mod %s -- %s' % (page.last_modified, page.last_modified > rows[0][1]))


    print('Complete')

def process_commands(commands):
    commands['index'] = index_command
    return commands


add_filter('commands', process_commands)