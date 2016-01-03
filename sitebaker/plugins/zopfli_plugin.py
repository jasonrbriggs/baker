import os
import pickle

from events import add_filter, apply_filter, do_action
from utils import *

def compress(dir, files, zopflipng, ext):
    count = 0
    for (root, src) in find_files(dir, False, ext):
        f = os.path.join(root, src)
        src_st = os.stat(f)
        last_mod = src_st.st_mtime
        
        if f in files:
            cmp_last_mod = files[f]
            if cmp_last_mod >= last_mod:
                continue
        
        target = f + ".tmp"
        call([zopflipng, f, target])
        
        tgt_st = os.stat(target)
        if tgt_st.st_size < src_st.st_size:
            os.remove(f)
            os.rename(target, f)
            count += 1
        else:
            os.remove(target)
            
        files[f] = last_mod
    return count

def zopfli_command(kernel, *args):
    zopflipng = which('zopflipng')
    if not zopflipng:
        print('Unable to compress with zopflipng - cmd not found')
        return
        
    print('Compressing files with zopflipng')
    
    if os.path.exists('.zopfli_files'):
        f = open('.zopfli_files', 'rb')
        files = pickle.load(f)
    else:
        files = {}
    
    count = 0
    count += compress(kernel.options.dir, files, zopflipng, '.png')
    
    f = open('.zopfli_files', 'wb')
    pickle.dump(files, f)
    print('    - %s files compressed' % count)
    

def process_commands(commands):
    commands['zopfli'] = zopfli_command
    return commands


add_filter('commands', process_commands)

