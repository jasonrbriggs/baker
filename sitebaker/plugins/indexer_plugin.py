import postgresql

from baker import add_filter

def index_command(kernel, *args):
    print('Indexing site...')
    for page in kernel.pages.values():
        print('  processing %s' % page.url)
    print('Complete')

def process_commands(commands):
    commands['index'] = index_command
    return commands


add_filter('commands', process_commands)
