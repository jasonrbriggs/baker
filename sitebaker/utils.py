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
            if os.path.getsize(target) > os.path.getsize(src):
                os.remove(target)

    def compress_files(self):
        self.compress('.jpg', '.jpggz')
        self.compress('.png', '.pnggz')
        self.compress('.css', '.cssgz')


class PluginManager:
    def __init__(self, folder):
        folder = os.path.abspath(folder)

        if not os.path.isdir(folder):
            raise RuntimeError("Unable to load plugins because '%s' is not a folder" % folder)

        # Append the folder because we need straight access
        sys.path.append(folder)

        # Build list of folders in directory
        to_import = [f for f in os.listdir(folder) if not f.endswith(".pyc") and not f.find('__pycache__') >= 0]

        # Do the actual importing
        for module in to_import:
            self.__initialize_plugin(module)

    def __initialize_plugin(self, module):
        '''
        Attempt to load the definition.
        '''

        # Import works the same for py files and package modules so strip!
        if module.endswith(".py"):
            name = module [:-3]
        else:
            name = module

        # Do the actual import
        __import__(name)
        print("Loaded %s" % name)

    def new_instance(self, name, *args, **kwargs):
        '''
        Creates a new instance of a definition
        name - name of the definition to create
 
        any other parameters passed will be sent to the __init__ function
        of the definition, including those passed by keyword
        '''

        definition = self.definitions[name]
        return getattr(definition, definition.info["class"])(*args, **kwargs)


def find_files(dir, sort=True, *exts):
    rtn = [ ]
    for root, dirs, files in os.walk(dir):
        for name in files:
            if matches_exts(name, exts):
                rtn.append((root, name))
    if sort:
        rtn.sort(key = lambda x : os.path.getmtime(os.path.join(x[0], x[1])))
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
            os.mkdirs(target_path)

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


def load_configs(dir):
    configs = { }
    length = len(dir)
    for root, name in find_files(dir, False, '.ini'):
        path = os.path.join(root, name)
        name = os.path.dirname(path[length:])

        config = configparser.ConfigParser()
        config.read_file(open(path))

        parent_config = find_parent_config(configs, name)
        config.parent = parent_config
        configs[name] = config

    configparser.ConfigParser.originalget = configparser.ConfigParser.get
    configparser.ConfigParser.original_has_option = configparser.ConfigParser.has_option
    configparser.ConfigParser.get = get_option
    configparser.ConfigParser.has_option = has_option
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
        setattr(parser.values,option.dest,val)
    return func


def url_join(path1, path2):
    if path1.endswith('/') and path2.startswith('/'):
        return path1[0:len(path1)-1] + path2
    elif not path1.endswith('/') and not path2.startswith('/'):
        return path1 + '/' + path2
    else:
        return path1 + path2