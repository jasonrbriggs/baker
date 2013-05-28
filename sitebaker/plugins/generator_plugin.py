import datetime
import os

from events import add_filter, apply_filter, do_action
import utils
import __init__


def generate(kernel, *args):
    """
    Performs the following actions:
    1. load pages
    2. generate the output for each page
    3. apply the 'pages' global filter for all pages
    4. compress any applicable files (images, etc)
    """
    print('Processing pages')
    for page in kernel.pages.values():
        generate_page(kernel, page)

    apply_filter('pages', kernel.pages, kernel.options.output)

    print('Compressing files')
    comp = utils.Compressor(kernel.options.dir, kernel.options.output)
    comp.compress_files()
    print('Generation complete')


def generate_page(kernel, page):
    """
    Internal generator called for each page which applies the following filters (before writing the html output):
    1. page-head
    2. page-meta
    3. page-markdown
    4. page-menu
    5. post-meta
    """
    if not page.template:
        return

    fname = page.url[1:] + '.html'
    output_path = os.path.join(page.output_path, fname)

    if os.path.exists(output_path):
        statbuf = os.stat(output_path)
        last_modified = datetime.datetime.fromtimestamp(statbuf.st_mtime)
    else:
        last_modified = datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')

    page.output_url = fname

    do_action('post-meta-reset')
    apply_filter('page-head', page)
    apply_filter('page-meta', page)
    apply_filter('page-markdown', page)
    apply_filter('page-menu', page)
    apply_filter('post-meta', page)
    apply_filter('page-foot', page)

    if last_modified > page.last_modified and kernel.options.force == 'false':
        return

    print('  - %s' % page.url)
    page.template.set_attribute('generator', 'content', 'SiteBaker v%s' % __init__.__version__)

    out = str(page.template)
    f = open(output_path, 'w+')
    f.write(out)
    f.close()


def process_commands(commands):
    commands['generate'] = generate
    return commands

add_filter('commands', process_commands)