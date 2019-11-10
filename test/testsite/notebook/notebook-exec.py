import sys
_baker_mpl = True

global image_counter
image_counter = 0

global block_name
block_name = ''

try:
    import matplotlib
    #matplotlib.use('Agg')
    import matplotlib.pyplot as _baker_plt

    def matplot_show(*args, **kw):
        global image_counter
        image_counter = image_counter + 1
        image_name = block_name + '-' + str(image_counter) + '.png'
        _baker_plt.savefig(image_name, figsize=(8, 6), dpi=80)
        _baker_plt.clf()

    _baker_plt.show = matplot_show
except ImportError:
    _baker_mpl = False

fout = open('notebook/notebook-pyblock-1.out', 'w'); ferr = open('notebook/notebook-pyblock-1.err', 'w'); sys.stdout = fout; sys.stderr = ferr
block_name = 'notebook/notebook-pyblock-1'

print('hello')

fout.close(); ferr.close()
fout = open('notebook/notebook-pyblock-2.out', 'w'); ferr = open('notebook/notebook-pyblock-2.err', 'w'); sys.stdout = fout; sys.stderr = ferr
block_name = 'notebook/notebook-pyblock-2'

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 3*np.pi, 500)
plt.plot(x, np.sin(x**2))
plt.title('A simple chirp')
plt.show()

fout.close(); ferr.close()