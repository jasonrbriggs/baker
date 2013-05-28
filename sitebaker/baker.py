import os
import sys

from proton import template

import utils
from pages import load_pages
from events import apply_filter

class Kernel:
    def __init__(self, options):
        self.options = options
        template.base_dir = os.path.join(options.dir, 'theme')
        self.configs = utils.load_configs(options.dir)

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

    def help(self):
        for command in self.commands:
            cmd = command.ljust(10, ' ')
            print('%s\ttodo (help text here)' % cmd)

    def run_command(self, command, *args):
        if command not in self.commands:
            print('No such command')
            sys.exit(1)
        else:
            self.commands[command](self, *args)