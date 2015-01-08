# -*- coding: utf-8 -*-
"""
Created on Mon Sep 01 10:56:04 2014

@author: Florian LE BOURDAIS
"""

import sys

from generate_readme import filename2url

if __name__ == "__main__":
    try:    
        nb_name = sys.argv[1]
        print("""This post was entirely written using the IPython notebook. Its content is BSD-licensed. You can see a static view or download this notebook with the help of nbviewer at [{0}]({1}).""".format(nb_name, filename2url(nb_name)))
    except:
        print("Usage: python generate_notebook_header_footer.py notebook_name")
