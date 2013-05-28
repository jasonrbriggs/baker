from events import add_filter


def version(kernel, *args):
    """
    Display SiteBaker version info.
    """
    print('sitebaker version %s' % kernel.version)


def process_commands(commands):
    commands['version'] = version
    return commands

add_filter('commands', process_commands)