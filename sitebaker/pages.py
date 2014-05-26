import datetime
import os
import re

from events import apply_filter
from proton import template

import utils

title_end_re = re.compile(r'^\-+\s*$')


class Page:
    def __init__(self, kernel=None, path=None, output_path=None, url=None, config=None):
        self.kernel = kernel
        self.url = url
        self.output_url = None
        self.output_path = output_path
        self.full_content = None
        self.fmt_last_modified = None

        if path:
            name = os.path.basename(path)[0:-5]
            self.full_content = open(path).read()
            statbuf = os.stat(path)
            self.last_modified = datetime.datetime.fromtimestamp(statbuf.st_mtime)
            self.fmt_last_modified = self.last_modified.strftime('%d %b, %Y')
        self.headers = {}
        self.config = config

        if self.full_content:
            pos = self.full_content.find('\n\n')
            if pos >= 0:
                tmp = self.full_content[0:pos]
                for line in tmp.split('\n'):
                    kvpos = line.find(':')
                    if kvpos > 0:
                        key = line[0:kvpos].strip()
                        val = line[kvpos+1:].strip()
                        self.headers[key] = val
            if len(self.headers):
                self.content = self.full_content[pos:]
            else:
                self.content = self.full_content

        template_name = None
        if 'template' in self.headers:
            template_name = self.headers['template']
        elif self.config:
            template_name = self.config.get('templates', name)

        if not template_name and self.config:
            template_name = self.config.get('templates', 'default')

        if template_name:
            self.template = template.get_template(template_name)

        if 'posted-on' in self.headers:
            self.fmt_last_modified = self.headers['posted-on']

        # default to html content (TODO: probably should handle this better)
        if url is not None:
            self.filename = url[1:] + '.html'
            self.full_output_path = os.path.join(output_path, self.filename)
        else:
            self.filename = None
            self.full_output_path = None

    def copy(self, other_page):
        self.kernel = other_page.kernel
        self.url = other_page.url
        self.full_content = other_page.full_content
        self.content = other_page.content
        self.headers = other_page.headers
        self.template = other_page.template
        self.config = other_page.config

    def get_permalink(self):
        domain = self.config.get('site', 'domain')
        return 'http://%s%s' % (domain, self.url)

    def get_posted_date(self):
        if 'posted-on' in self.headers:
            return self.headers['posted-on']
        elif self.fmt_last_modified:
            return self.fmt_last_modified
        else:
            return None

    def get_html_content(self, include_title=False):
        domain = self.config.get('site', 'domain')
        if not include_title:
            if title_end_re.search(self.content) is not None:
                content = remove_title(content)
            else:
                content = self.content
        else:
            content = self.content
        html_content = apply_filter('markdown', content)
        return html_content.replace('src="/', 'src="http://%s/' % domain)

    def __str__(self):
        return 'url=%s,updated=%s' % (self.get_permalink(), self.get_posted_date())


def filter_pages(path, pages):
    for page in pages:
        if page.url.startswith(path):
            yield page

def remove_title(content):
    lines = content.split('\n')
    for x in range(0, len(lines)):
        if lines[x].rstrip() == '':
            print('continue')
            continue
        if not title_end_re.match(lines[x]) and title_end_re.match(lines[x+1]):
            return '\n'.join(lines[x+2:])
        else:
            return content
            

def load_pages(directory, output_path, kernel):
    """
    Find all .text files in the specified directory and return a map of Page objects, keyed by the
    url for the page.

    \param directory
        starting directory to search
    \param output_path
        the directory we'll be writing output to
    \param configs
        the config map which we'll use to get the template for each page
    \param templates
        the Templates singleton
    """
    page_map = {}
    length = len(directory)
    for root, name in utils.find_files(directory, False, '.text'):
        path = os.path.join(root, name)
        base_path = root[length:]
        if not base_path.startswith('/'):
            base_path = '/' + base_path
        name = name[0:-5]

        url = utils.url_join(base_path, name)
        config = utils.find_config(kernel.configs, base_path)
        page = Page(kernel, path, output_path, url, config)
        page_map[url] = page

    return page_map


def get_root_page(pages, section=None):
    """
    Return the root page of the pages map.
    """
    if len(pages.values()) == 0:
        return None
    root_page = list(pages.values())[0]
    if section and not root_page.config.has_section(section):
        return None
    return root_page
