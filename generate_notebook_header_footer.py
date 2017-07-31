# -*- coding: utf-8 -*-
"""
Created on Mon Sep 01 10:56:04 2014

@author: Florian LE BOURDAIS
"""

import sys
if sys.version_info >= (3, 0):
    from urllib.parse import quote
else:
    from urllib import quote

def filename2url(filename):
    return "http://nbviewer.ipython.org/urls/raw.github.com/flothesof/posts/master/{0}".format(
                                                                        quote(filename))

if __name__ == "__main__":
    try:    
        nb_name = sys.argv[1]
        print("""*This post was entirely written using the IPython notebook. Its content is BSD-licensed. You can see a static view or download this notebook with the help of nbviewer at [{0}]({1}).*""".format(nb_name, filename2url(nb_name)))
        
        print("""*Ce billet a été écrit à l'aide d'un notebook Jupyter. Son contenu est sous licence BSD. Une vue statique de ce notebook peut être consultée et téléchargée ici : [{0}]({1}).*""".format(nb_name, filename2url(nb_name)))
        
    except:
        print("Usage: python generate_notebook_header_footer.py notebook_name")
