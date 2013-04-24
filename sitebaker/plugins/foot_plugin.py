from baker import add_filter
from proton import template

def process(page):
    # include the head
    if 'foot' in page.headers:
        tmp = template.get_template(page.headers['foot'])
        page.template.replace('foot', tmp)
    elif page.config.has_option('templates', 'foot'):
        tmp = template.get_template(page.config.get('templates', 'foot'))
        page.template.replace('foot', tmp)
    return page

add_filter('page-foot', process)