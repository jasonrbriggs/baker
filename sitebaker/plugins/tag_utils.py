import re

split_re = re.compile(r'\s*,\s*')

def sanitise_tag(tag):
    return tag.replace(' ', '-')

def split_tags(tags):
    return split_re.split(tags)