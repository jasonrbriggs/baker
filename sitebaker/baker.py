import os
import sys

from proton import template

import utils
from pages import load_pages
from events import apply_filter

import __init__


class PluginManager:
    def __init__(self, folders):
        to_imp = []
        for folder in folders:
            folder = os.path.abspath(folder)

            if not os.path.isdir(folder):
                raise RuntimeError("Unable to load plugins because '%s' is not a folder" % folder)

            # Append the folder because we need straight access
            sys.path.append(folder)

            # Build list of folders in directory
            to_import = [f for f in os.listdir(folder) if not f.endswith(".pyc") and not f.find('__pycache__') >= 0]
            to_imp += to_import

        # Do the actual importing
        for module in to_imp:
            self.__initialize_plugin(module)

    def __initialize_plugin(self, module):
        """
        Attempt to load the definition.
        """

        # Import works the same for py files and package modules so strip!
        if module.endswith(".py"):
            name = module[:-3]
        else:
            name = module

        # Do the actual import
        __import__(name)

    def new_instance(self, name, *args, **kwargs):
        """
        Creates a new instance of a definition
        name - name of the definition to create

        any other parameters passed will be sent to the __init__ function
        of the definition, including those passed by keyword
        """
        definition = self.definitions[name]
        return getattr(definition, definition.info["class"])(*args, **kwargs)


class Kernel:
    def __init__(self, options):
        self.options = options
        self.version = __init__.__version__
        plugin_folders = [os.path.join(sys.path[0], 'plugins')]

        if os.path.exists('site.ini'):
            template.base_dir = os.path.join(options.dir, 'theme')
            self.verbose_log('Loading configuration files')
            self.configs = utils.load_configs(options.dir)
            config = utils.find_config(self.configs, '/')
            if config is not None:
                plugin_path = config.get('control', 'plugins_path')
                if plugin_path is not None:
                    plugin_folders.append(os.path.join(os.getcwd(), plugin_path))

        self.verbose_log('Initialising plugin manager')
        self.pm = PluginManager(plugin_folders)
        self.verbose_log('    - complete')

        if os.path.exists('site.ini'):
            self.verbose_log('Loading pages')
            self.pages = load_pages(options.dir, options.output, self)
            self.verbose_log('    - complete')
        self.commands = {}
        self.verbose_log('Running commands filter')
        apply_filter('commands', self.commands)

    def verbose_log(self, msg):
        if self.options.verbose == 'true':
            print(msg)

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