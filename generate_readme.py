# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# The goal of this notebook is to generate a file containing links to all notebooks in my posts directory for easy access from the web.
# 
# The link that helped me encode the urls with percent encoding is the following : [http://stackoverflow.com/questions/1695183/how-to-percent-encode-url-parameters-in-python](http://stackoverflow.com/questions/1695183/how-to-percent-encode-url-parameters-in-python).

# <codecell>

import os

# <codecell>

files = os.listdir(os.getcwd())
files = filter(lambda s: s.endswith('.ipynb'), files)
files

# <codecell>

import urllib

# <codecell>

urllib.quote(files[1])

# <codecell>

with open('notebooks_links.md', 'w') as f:
    f.write("""# Links to all the notebooks in this folder to be statically viewed on nbviewer\n\n""")
    for filename in files:
        f.write("[%s](http://nbviewer.ipython.org/urls/raw.github.com/flothesof/posts/master/%s)\n" % (filename, urllib.quote(filename)))

