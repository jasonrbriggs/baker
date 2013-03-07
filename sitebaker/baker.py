import os
import sys

from proton.template import Templates

import utils
import pages
import __init__


def load_pages(dir, output_path, configs, templates):
    '''
    Find all .text files in the specified directory and return a map of Page objects, keyed by the
    url for the page.

    \param dir
        starting directory to search
    \param output_path
        the directory we'll be writing output to
    \param configs
        the config map which we'll use to get the template for each page
    \param templates
        the Templates singleton
    '''
    page_map = { }
    length = len(dir)
    for root, name in utils.find_files(dir, False, '.text'):
        path = os.path.join(root, name)
        base_path = root[length:]
        if not base_path.startswith('/'):
            base_path = '/' + base_path
        name = name[0:-5]

        url = utils.url_join(base_path, name)
        config = utils.find_config(configs, base_path)
        page = pages.Page(path, output_path, url, config)
        page_map[url] = page

    return page_map


def add_filter(name, plugin):
    '''
    Add a filter (similar idea to WordPress's add_filter/action).

    \param name
        the name of the filter
    \param plugin
        the callable we'll invoke for this filter
    '''

    if name not in __init__.__filters__:
        __init__.__filters__[name] = [ ]
    __init__.__filters__[name].append(plugin)


def apply_filter(name, *args):
    '''
    Run the code for a filter.

    \param name
        the name of the filter
    \param args
        the set of arguments to pass to the plugin/callable
    '''
    my_args = list(args)
    rtn = None
    if name in __init__.__filters__:
        plugins = __init__.__filters__[name]
        for plugin in plugins:
            rtn = plugin(*my_args)
            my_args[0] = rtn
    return rtn

def add_action(name, plugin):
    '''
    Add an action (similar idea to WordPress's add_action/do_action).

    \param name
        the name of the action
    \param plugin
        the callable we'll invoke for this action
    '''

    if name not in __init__.__actions__:
        __init__.__actions__[name] = [ ]
    __init__.__actions__[name].append(plugin)

def do_action(name, *args):
    '''
    Run the code for an action.

    \param name
        the name of the action
    \param args
        the set of arguments to pass to the plugin/callable
    '''
    if name in __init__.__actions__:
        plugins = __init__.__actions__[name]
        for plugin in plugins:
            plugin(*args)


class Kernel:
    def __init__(self, options):
        self.options = options
        self.templates = Templates(os.path.join(options.dir, 'theme'))
        self.configs = utils.load_configs(options.dir)
        self.pm = utils.PluginManager(os.path.join(sys.path[0], 'plugins'))
        self.pages = load_pages(options.dir, options.output, self.configs, self.templates)
        self.commands = { }
        apply_filter('commands', self.commands)

    def help(self):
        for command in self.commands:
            cmd = command.ljust(10, ' ')
            print('%s\ttodo (help text here)' % cmd)

    def run_command(self, command, *args):
        if command not in self.commands:
            print('No such command')
            sys.exit(1)
        else:
            self.commands[command](self, args)