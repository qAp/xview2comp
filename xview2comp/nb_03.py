
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/03_damage_classification.ipynb

from xview2comp.nb_02c import *

def combine_nodamage_unclassified(annots):
    base_level = 'no-damage/un-classified'
    df = annots.copy()
    df.damage.replace('no-damage', base_level, inplace=True)
    df.damage.replace('un-classified', base_level, inplace=True)
    return df

def get_label(annots, fname):
    return annots[annots.uid == fname.stem].damage.values[0]