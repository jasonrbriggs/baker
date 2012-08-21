from baker import add_filter

def process(page):
    if 'head' in page.headers:
        page.template.include('head', page.headers['head'])
    elif page.config.has_option('templates', 'head'):
        page.template.include('head', self.config.get('templates', 'head'))

    if page.config.has_option('templates', 'header'):
        page.template.include('header', page.config.get_value(srcdir, 'templates', 'header'))

    for key,val in page.headers.items():
        page.template.setelement(key, val)

add_filter('template-processor', process)