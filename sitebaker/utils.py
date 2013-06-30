import configparser
import gzip
import os
import sys


class Compressor:
    def __init__(self, source, target):
        self.source = source
        self.target = target

    def compress(self, src_ext, tgt_ext):
        for src, target in find_changed_files(self.source, src_ext, self.target, tgt_ext):
            with open(src, 'rb') as f_in:
                with gzip.open(target, 'wb', 9) as f_out:
                    f_out.writelines(f_in)

    def compress_files(self):
        self.compress('.jpg', '.jpggz')
        self.compress('.css', '.cssgz')


def find_files(directory, sort=True, *exts):
    rtn = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            if matches_exts(name, exts):
                rtn.append((root, name))
    if sort:
        rtn.sort(key=lambda x: os.path.getmtime(os.path.join(x[0], x[1])))
    return rtn


def find_changed_files(source_dir, source_ext, target_dir, target_ext):
    src_ext_len = len(source_ext)
    src_len = len(source_dir)
    for root, name in find_files(source_dir, False, source_ext):
        base_name = name[0:-src_ext_len]

        source_name = os.path.join(root, name)
        subdir = root[src_len+1:]

        target_path = os.path.join(target_dir, subdir)
        target_name = os.path.join(target_path, base_name + target_ext)

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        if not os.path.exists(target_name) or os.stat(source_name).st_mtime > os.stat(target_name).st_mtime:
            yield (source_name, target_name)


def find_config(configs, path):
    if path in configs:
        return configs[path]
    parent_path = os.path.dirname(path)
    if parent_path == path:
        return None
    else:
        return find_config(configs, parent_path)


def find_parent_config(configs, path):
    parent_path = os.path.dirname(path)
    if parent_path == path:
        return None
    elif parent_path in configs:
        return configs[parent_path]
    else:
        return find_parent_config(configs, parent_path)


def get_option(conf, section, option):
    if conf.original_has_option(section, option):
        return conf.originalget(section, option)
    elif conf.parent is not None:
        return get_option(conf.parent, section, option)
    else:
        return None


def has_option(conf, section, option):
    if conf.original_has_option(section, option):
        return True
    elif conf.parent is not None:
        return has_option(conf.parent, section, option)
    else:
        return None


def has_section(conf, section):
    if conf.original_has_section(section):
        return True
    elif conf.parent is not None:
        return has_section(conf.parent, section)
    else:
        return None


def items(conf, section):
    if conf.original_has_section(section):
        return conf.original_items(section)
    elif conf.parent is not None:
        return items(conf.parent, section)
    else:
        return []


def load_configs(directory):
    configs = {}
    length = len(directory)
    for root, name in find_files(directory, False, '.ini'):
        path = os.path.join(root, name)
        name = os.path.dirname(path[length:])

        config = configparser.ConfigParser()
        config.read_file(open(path))

        parent_config = find_parent_config(configs, name)
        config.parent = parent_config
        configs[name] = config

    configparser.ConfigParser.originalget = configparser.ConfigParser.get
    configparser.ConfigParser.original_has_option = configparser.ConfigParser.has_option
    configparser.ConfigParser.original_has_section = configparser.ConfigParser.has_section
    configparser.ConfigParser.original_items = configparser.ConfigParser.items
    configparser.ConfigParser.get = get_option
    configparser.ConfigParser.has_option = has_option
    configparser.ConfigParser.has_section = has_section
    configparser.ConfigParser.items = items
    return configs


def matches_exts(name, *exts):
    for ext in exts:
        if name.endswith(ext):
            return True
    return False


def optional_arg(arg_default):
    def func(option, opt_str, value, parser):
        if parser.rargs and not parser.rargs[0].startswith('-'):
            val = parser.rargs[0]
            parser.rargs.pop(0)
        else:
            val = arg_default
        setattr(parser.values, option.dest,val)
    return func


def __url_join(path1, path2):
    if path1.endswith('/') and path2.startswith('/'):
        return path1[0:len(path1)-1] + path2
    elif not path1.endswith('/') and not path2.startswith('/'):
        return path1 + '/' + path2
    else:
        return path1 + path2


def url_join(*args):
    if len(args) == 0:
        return ''
    elif len(args) == 1:
        return args[0]
    else:
        return url_join(*(__url_join(args[0], args[1]),) + args[2:])
