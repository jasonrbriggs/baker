import sys

from events import add_filter


def help(kernel, *args):
    """
    Display help for a specific command.
    """
    if len(args) <= 0 or len(args[0]) <= 0:
        print('Please provide the command you want to display help for')
        sys.exit(1)
    cmd = args[0][0]
    if cmd not in kernel.commands:
        print('"%s" is not a recognised command' % cmd)
        sys.exit(1)
    print(kernel.commands[cmd].__doc__)


def process_commands(commands):
    commands['help'] = help
    return commands

add_filter('commands', process_commands)