import datetime
import os
import re
import time

import markdown2
from proton import template

title_end_re = re.compile(r'-(-+)\s*')

class Page:
    def __init__(self, kernel = None, path = None, output_path = None, url = None, config = None):
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
        self.headers = { }
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
            self.last_modified = datetime.datetime.strptime(self.headers['posted-on'], '%d %b, %Y')
            self.fmt_last_modified = self.headers['posted-on']

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
            content = self.content[title_end_re.search(self.content).end():]
        else:
            content = self.content
        html_content = markdown2.markdown(content, extras=['fenced-code-blocks'])
        return html_content.replace('src="/', 'src="http://%s/' % domain)

    def __str__(self):
        return 'url=%s,updated=%s' % (self.get_permalink(), self.get_posted_date())

def filter_pages(path, pages):
    for page in pages:
        if page.url.startswith(path):
            yield page
