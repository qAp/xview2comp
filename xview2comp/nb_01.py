
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/01_load_data.ipynb

import sys
sys.path.append('/Users/jack/git_repos/course-v3/nbs/dl2')
from exp.nb_12a import *

import os, json, sys
from pathlib import Path
import numpy as np, pandas as pd
import PIL, geopandas as gpd, cv2
import shapely.wkt, shapely.geometry

import matplotlib.pyplot as plt

Path.ls = lambda o: list(o.iterdir())

def pre_img_fpaths(ns): return [Path(n) for n in ns if '_pre_' in str(n) and n.suffix=='.png']

def pre2post_fpath(o:Path): return Path(str(o).replace('_pre_', '_post_'))

def img2label_fpath(o:Path):
    return Path(str(o).replace('images/', 'labels/').replace('.png', '.json'))

def dict2srs_feature(o:dict):
    '''Convert a single feature's dict to series.'''
    d = dict()
    d.update(o['properties'])
    d.update({'wkt': o['wkt']})
    return pd.Series(d)

def features2df(fs:list):
    '''Convert all features' dict to series, return dataframe.'''
    assert len(fs) > 0
    df = pd.DataFrame()
    for f in fs: df = df.append(feature2srs(f), ignore_index=True)
    df['geometry'] = df.wkt.apply(shapely.wkt.loads)
    df.drop('wkt', axis=1, inplace=True)
    return df

def polys2mask(ps:list, sz=(1024, 1024)):
    '''Convert a list of shapely polygons to a binary mask. '''
    ps = [shapely.geometry.mapping(p) for p in ps]
    ps = [np.array(p['coordinates'][0], dtype=np.int32) for p in ps]
    ps = np.array(ps)

    img0 = np.zeros(sz, dtype=np.uint8)
    mask = cv2.fillPoly(img0, ps, (1,))
    mask[mask > 1] = 0
    return mask

def save_mask(m, fn): PIL.Image.fromarray(m).save(fn)
def load_mask(fn): return np.array(PIL.Image.open(fn))

def compose(x, funcs, *args, order_key='_order', **kwargs):
    key = lambda o: getattr(o, order_key, 0)
    for f in sorted(listify(funcs), key=key): x = f(x, **kwargs)
    return x

class ItemList(ListContainer):
    def __init__(self, items, path='.', tfms=None):
        super().__init__(items)
        self.path, self.tfms = Path(path), tfms

    def __repr__(self): return f'{super().__repr__()}\nPath: {self.path}'
    def new(self, items, cls=None):
        if cls is None: cls = self.__class__
        return cls(items, self.path, tfms=self.tfms)

    def get(self, i): return i
    def _get(self, i): return compose(self.get(i), self.tfms)
    def __getitem__(self, idx):
        res = super().__getitem__(idx)
        if isinstance(res, list): return [self._get(o) for o in res]
        return self._get(res)

class ImageList(ItemList):
    @classmethod
    def from_files(cls, path, extensions=None, recurse=True, include=None, **kwargs):
        if extensions is None: extensions = image_extensions
        return cls(get_files(path, extensions, recurse=recurse, include=include), path, **kwargs)

    def get(self, fn): return PIL.Image.open(fn)

class Transform(): _order = 0
class MakeRGB(Transform):
    def __call__(self, o): return o.convert('RGB')
def make_rgb(o): return o.convert('RGB')

class RandomSplitter(Transform):
    def __init__(self, val_pct=.1): self.val_pct = val_pct
    def __call__(self, il):
        n = len(il)
        idxs = np.random.permutation(n)
        cut = int(self.val_pct * n)
        items = ItemList(il.items)
        return il.new(items[idxs[:cut]]), il.new(items[idxs[cut:]])

class SplitData():
    def __init__(self, train, valid):
        self.train, self.valid = train, valid
    def __getattr__(self, k): return getattr(self.train, k)
    def __setstate__(self, data:Any): self.__dict__.update(data)
    @classmethod
    def split_by_func(cls, il, f):
        lists = map(il.new, split_by_func(il.items, f))
        return cls(*lists)
    @classmethod
    def split_by_random(cls, il, val_pct=.1):
        valid, train = RandomSplitter(val_pct)(il)
        return cls(train, valid)
    def __repr__(self):
        return f'{self.__class__.__name__}\nTrain: {self.train}\nValid: {self.valid}\n'

def _label_by_func(il, f, listtype=ItemList):
    return listtype([f(o) for o in il.items], path=il.path, tfms=il.tfms)

class LabeledData():
    def __init__(self, x, y): self.x, self.y = x, y
    def __getitem__(self, i): return self.x[i], self.y[i]
    def __len__(self): return len(self.x)
    @classmethod
    def label_by_func(cls, il, f, **kwargs):
        return cls(il, _label_by_func(il, f, **kwargs))
    def __repr__(self): return f'{self.__class__.__name__}\nx: {self.x}\ny: {self.y}\n'

def label_by_func(sd, f, **kwargs):
    train = LabeledData.label_by_func(sd.train, f, **kwargs)
    valid = LabeledData.label_by_func(sd.valid, f, **kwargs)
    return SplitData(train, valid)

def to_byte_tensor(o):
    _order = 20
    res = torch.ByteTensor(torch.ByteStorage.from_buffer(o.tobytes()))
    w, h = o.size
    return res.view(h, w, -1).permute(2, 0, 1)

def to_float_tensor(o):
    _order = 30
    return o.float().div_(255.)

class ResizeFixed(Transform):
    _order = 10
    def __init__(self, size):
        if isinstance(size, int): size = (size, size)
        self.size = size
    def __call__(self, o):
        if isinstance(o, PIL.Image.Image):
            return o.resize(self.size, PIL.Image.BILINEAR)
        if isinstance(o, PIL.PngImagePlugin.PngImageFile):
            return o.resize(self.size, PIL.Image.NEAREST)
        return o

def show_sample(img, mas, figsize=(3, 3)):
    _, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    ax.imshow(img.permute(1, 2, 0))
    ax.imshow(tensor([255, 30, 0.]) * mas.permute(1, 2, 0), alpha=.3)

class DataBunch():
    def __init__(self, train_dl, valid_dl):
        self.train_dl, self.valid_dl = train_dl, valid_dl

    @property
    def train_ds(self): return self.train_dl.dataset
    @property
    def valid_ds(self): return self.valid_dl.dataset

def databunchify(sd, bs, **kwargs):
    dls = get_dls(sd.train, sd.valid, bs, **kwargs)
    return DataBunch(*dls)

SplitData.to_databunch = databunchify