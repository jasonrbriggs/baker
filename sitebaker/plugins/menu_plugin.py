from baker import add_filter

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
                page.template.setelement('menulink', titlecfg, x)
            else:   
                page.template.setelement('menulink', id, x)
            page.template.setattribute('menulink', 'id', id, x)
            page.template.setattribute('menulink', 'href', link, x)
            x += 1
            
add_filter('page-menu', process)