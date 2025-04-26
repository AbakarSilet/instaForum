from unidecode import unidecode
import re
from django.db import models
from django.utils.translation import gettext_lazy as _


def remove_accents(input_str):
    return unidecode(input_str)



def normalize_tag(tag):
    """
    Normalise un tag en retirant les accents, 
    convertissant en minuscules et nettoyant
    """
    # Convertir en minuscules
    tag = tag.lower()
    
    # Retirer les accents
    tag = unidecode(tag)
    
    # Nettoyer (supprimer les caractères spéciaux)
    tag = re.sub(r'[^\w\s-]', '', tag)
    
    # Remplacer les espaces par des tirets
    tag = re.sub(r'[-\s]+', '-', tag).strip('-')
    
    return tag

def normalize_tags(tags):
    """
    Normalise une liste de tags
    """
    return [normalize_tag(tag) for tag in tags]
