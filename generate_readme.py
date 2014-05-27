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
header = """posts
=====

This is a sort of blog / work in progress repository for interesting projects that pop into my mind.

![files/xkcd_departments.png](files/xkcd_departments.png)

"""
with open('README.md', 'w') as f:
    f.write(header)
    for index, filename in enumerate(files):
        f.write("- [%i-%s](http://nbviewer.ipython.org/urls/raw.github.com/flothesof/posts/master/%s)\n" % (index + 1, 
                                                        filename, urllib.quote(filename)))

