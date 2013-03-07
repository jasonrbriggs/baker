import os
import time

from proton.template import Templates
from baker import add_filter


def process(pages, output_path):
    tmp = Templates._singleton['sitemap.xml']
    if not tmp:
        return
    tmp.repeat('urls', len(pages))
    x = 0

    for page in sorted(pages):
        pg = pages[page]
        domain = pg.config.get('site', 'domain')
        tmp.setelement('url', 'http://' + domain + '/' + pg.output_url, x)
        tmp.setelement('lastmod', pg.last_modified.strftime('%Y-%m-%d'), x)
        x += 1

    out = str(tmp)
    f = open(os.path.join(output_path, 'sitemap.xml'), 'w+')
    f.write(out)
    f.close()
    return pages


add_filter('pages', process)