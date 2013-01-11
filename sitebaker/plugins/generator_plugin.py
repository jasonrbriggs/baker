import os

from baker import add_filter, apply_filter, do_action
import utils
import __init__

def generate(kernel, *args):
    '''
    Performs the following actions:
    1. load pages
    2. generate the output for each page
    3. apply the 'pages' global filter for all pages
    4. compress any applicable files (images, etc)
    '''
    print('Processing pages')
    for page in kernel.pages.values():
        generate_page(page)

    print('Applying pages filter')
    apply_filter('pages', kernel.pages, kernel.options.output)

    print('Compressing files')
    comp = utils.Compressor(kernel.options.dir, kernel.options.output);
    comp.compress_files()
    print('Generation complete')

def generate_page(page):
    '''
    Internal generator called for each page which applies the following filters (before writing the html output):
    1. page-head
    2. page-meta
    3. page-markdown
    4. page-menu
    5. post-meta
    '''
    print('Processing %s' % page.url)
    do_action('post-meta-reset')
    apply_filter('page-head', page)
    apply_filter('page-meta', page)
    apply_filter('page-markdown', page)
    apply_filter('page-menu', page)
    apply_filter('post-meta', page)
    apply_filter('page-foot', page)

    page.template.setattribute('generator', 'content', 'SiteBaker v%s' % __init__.__version__)

    fname = page.url[1:] + '.html'

    page.output_url = fname

    out = str(page.template)
    f = open(os.path.join(page.output_path, fname), 'w+')
    f.write(out)
    f.close()

def process_commands(commands):
    commands['generate'] = generate

add_filter('commands', process_commands)