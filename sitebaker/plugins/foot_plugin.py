from baker import add_filter

def process(page):
    # include the head
    if 'foot' in page.headers:
        page.template.include('foot', page.headers['foot'])
    elif page.config.has_option('templates', 'foot'):
        page.template.include('foot', page.config.get('templates', 'foot'))
    return page

add_filter('page-foot', process)