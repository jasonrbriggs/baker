import os
import sys

from proton import template

import utils
from pages import load_pages
from events import apply_filter

import __init__


class Kernel:
    def __init__(self, options):
        self.options = options
        template.base_dir = os.path.join(options.dir, 'theme')
        self.configs = utils.load_configs(options.dir)
        self.version = __init__.__version__

        config = utils.find_config(self.configs, '/')
        plugin_folders = [os.path.join(sys.path[0], 'plugins')]
        if config is not None:
            plugin_path = config.get('control', 'plugins_path')
            if plugin_path is not None:
                plugin_folders.append(os.path.join(os.getcwd(), plugin_path))

        self.pm = utils.PluginManager(plugin_folders)
        self.pages = load_pages(options.dir, options.output, self)
        self.commands = {}
        apply_filter('commands', self.commands)

    def usage(self):
        print('''usage: baker [--force] <command> [<args>]

Available commands are:''')
        for command in self.commands:
            if self.commands[command].__doc__ is not None:
                doc = self.commands[command].__doc__.lstrip().rstrip()
                doc = doc.split("\n")
                usage_text = doc[0]
            else:
                usage_text = ''
            cmd = command.ljust(10, ' ')
            print('   %s\t%s' % (cmd, usage_text))

    def run_command(self, command, *args):
        if command not in self.commands:
            print('No such command')
            sys.exit(1)
        else:
            self.commands[command](self, *args)