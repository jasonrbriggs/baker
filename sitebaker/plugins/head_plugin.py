from events import add_filter
from proton import template


def process(page):
    # include the head
    if 'head' in page.headers:
        tmp = template.get_template(page.headers['head'])
        page.template.replace('head', tmp)
    elif page.config.has_option('templates', 'head'):
        tmp = template.get_template(page.config.get('templates', 'head'))
        page.template.replace('head', tmp)

    if page.config.has_option('templates', 'header'):
        tmp = template.get_template(page.config.get('templates', 'header'))
        page.template.replace('header', tmp)
    return page
            
add_filter('page-head', process)