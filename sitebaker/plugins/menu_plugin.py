from events import add_filter


def process(page):
    menucfg = page.config.get('menu', 'menu')
    if menucfg:
        split = menucfg.split(',')
        page.template.repeat('menu', len(split))

        x = 0
        for item in split:
            (id, link) = item.split('=')
            title = '%s-title' % id
            titlecfg = page.config.get('menu', title)
            if titlecfg:
                page.template.set_value('menulink', titlecfg, x)
            else:   
                page.template.set_value('menulink', id, x)
            page.template.set_attribute('menulink', 'id', id, x)
            page.template.set_attribute('menulink', 'href', link, x)
            x += 1
    return page
            
add_filter('page-menu', process)