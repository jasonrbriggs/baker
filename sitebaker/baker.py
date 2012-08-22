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
        the callabale we'll invoke for this filter
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
    if name in __init__.__filters__:
        plugins = __init__.__filters__[name]
        for plugin in plugins:
            plugin(*args)


class Generator:

    def __init__(self, options):
        self.options = options
        self.templates = Templates(os.path.join(options.dir, 'theme'))
        self.configs = utils.load_configs(options.dir)
        self.pm = utils.PluginManager(os.path.join(sys.path[0], 'plugins'))

    def generate(self):
        '''
        Performs the following actions:
        1. load pages
        2. generate the output for each page
        3. apply the 'pages' global filter for all pages
        4. compress any applicable files (images, etc)
        '''
        pages = load_pages(self.options.dir, self.options.output, self.configs, self.templates)

        for page in pages.values():
            self.__generate(page)

        apply_filter('pages', pages, self.options.output)

        comp = utils.Compressor(self.options.dir, self.options.output);
        comp.compress_files()

    def __generate(self, page):
        '''
        Internal generator called for each page which applies the following filters (before writing the html output):
        1. page-head
        2. page-meta
        3. page-markdown
        4. page-menu
        5. post-meta
        '''
        apply_filter('page-head', page)
        apply_filter('page-meta', page)
        apply_filter('page-markdown', page)
        apply_filter('page-menu', page)
        apply_filter('post-meta', page)

        page.template.setattribute('generator', 'content', 'SiteBaker v%s' % __init__.__version__)

        out = str(page.template)
        f = open(os.path.join(page.output_path, page.url[1:] + '.html'), 'w+')
        f.write(out)
        f.close()
