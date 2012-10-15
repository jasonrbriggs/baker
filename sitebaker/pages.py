import os

from proton.template import Templates

class Page:
    def __init__(self, path = None, output_path = None, url = None, config = None):
        self.url = url
        self.output_path = output_path
        self.full_content = None
        if path:
            name = os.path.basename(path)[0:-5]
            self.full_content = open(path).read()
            statbuf = os.stat(path)
            self.last_modified = statbuf.st_mtime
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
            self.template = Templates._singleton[template_name]

    def copy(self, other_page):
        self.url = other_page.url
        self.full_content = other_page.full_content
        self.content = other_page.content
        self.headers = other_page.headers
        self.template = other_page.template
        self.config = other_page.config

def filter_pages(path, pages):
    for page in pages:
        if page.url.startswith(path):
            yield page
