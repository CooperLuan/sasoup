# coding: utf-8
from .parser import Parser, AjaxParser
from .baserules import xpath, xpaths, xpathz, search, dpath, base, addon, fields, which, ajaxurl, ajax, RespType
__version__ = '0.2.5'
__all__ = [
    'Parser', 'AjaxParser',
    'xpath', 'xpaths', 'xpathz',
    'search', 'dpath',
    'base', 'addon', 'fields', 'which',
    'ajaxurl', 'ajax',
    'RespType',
]
