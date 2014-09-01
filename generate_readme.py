# -*- coding: utf-8 -*-

import os
import urllib

def filename2url(filename):
    return "http://nbviewer.ipython.org/urls/raw.github.com/flothesof/posts/master/{0}".format(
                                                                        urllib.quote(filename))
if __name__ == "__main__":
    files = os.listdir(os.getcwd())
    files = filter(lambda s: s.endswith('.ipynb'), files)
    
    header = """posts
=====

This is a sort of blog / work in progress repository for interesting projects that pop into my mind.

![files/xkcd_departments.png](files/xkcd_departments.png)

"""
    with open('README.md', 'w') as f:
        f.write(header)
        for index, filename in enumerate(files):
            f.write("- [%i-%s](%s)\n" % (index + 1, 
                                    filename, 
                                    filename2url(filename)))

