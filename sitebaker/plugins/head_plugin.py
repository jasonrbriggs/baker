from baker import add_filter

def process(page):
    # include the head
    if 'head' in page.headers:
        page.template.include('head', page.headers['head'])
    elif page.config.has_option('templates', 'head'):
        page.template.include('head', page.config.get('templates', 'head'))

    if page.config.has_option('templates', 'header'):
        page.template.include('header', page.config.get('templates', 'header'))
    return page
            
add_filter('page-head', process)