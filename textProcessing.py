import glob
import json
import re
import nltk

from nltk.corpus import stopwords


# 1 - On enlève la ponctuation
def enlever_ponctuation(chaine):
    return re.sub(r"[^\w\s]", "", chaine)

# 2 - On enlève les mots vides
def enlever_mots_vides(chaine):
    return [mot for mot in chaine if mot not in stopwords.words("french")]

# 3 - Tokenisation des mots, on les sépare en mots
def tokenisation(chaine):
    return chaine.split()