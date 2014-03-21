# encoding: utf8
import traceback
import logging
import re
import copy
from StringIO import StringIO
from string import Formatter
from urllib import unquote, urlencode, quote
from urlparse import urlparse, parse_qsl, urlunparse

from .escape import xhtml_unescape
from .baserules import *
from .exceptions import InvalidPageError, TemplateParseError, TemplateNotFoundError, \
    FieldParseError, InvalidFieldError, InvalidRuleError

import yaml
from lxml import etree

parser = etree.HTMLParser()


def _utf8(s, from_encoding=None):
    return s.encode('utf-8') \
        if from_encoding is None \
        else s.decode(from_encoding).encode('utf-8')


def _strip(s):
    return s.strip(' \r\t\n')


def _unescape(s):
    return _utf8(xhtml_unescape(s))


def gen_tree(html):
    """generate lxml.etree object from html"""
    return etree.parse(StringIO(html), parser)


def _cls_name(cls):
    """get object class name"""
    return cls.__class__.__name__


def _fmt_json_str(j_str):
    """format json string to standard json string"""
    j_str = j_str.replace('\t', '')
    j_str = j_str.replace(r'\/', '/')
    j_str = re.sub(r'\s+', r' ', j_str, re.S)
    j_str = re.sub(r':', r': ', j_str, re.S)
    j_str = re.sub(r':', r': ', j_str, re.S)
    j_str = j_str.replace(':', ': ')
    j_str = re.sub(r'(?P<pre>http:)\s+(?P<end>\/\/)', r'\g<pre>\g<end>', j_str, re.S)
    return j_str


def get_format_keys(fields_global, s):
    """get keys from str for format method of str"""
    return [t[1] for t in Formatter().parse(s) if t[1] and t[1] in fields_global]


def format_rule(fields_global, rule_str):
    """fill str with fields_global"""
    keys = get_format_keys(fields_global, rule_str)
    maps = dict((k, fields_global.get(k, None)) for k in keys)
    if maps:
        return rule_str.format(**maps)
    return rule_str


def parse_search(html, rule, fields_global={}):
    if rule is None or not rule.regx:
        return html
    if not html:
        return None
    s = re.search(format_rule(fields_global, rule.regx), html, re.S)
    if rule.resp == 'json':
        rule._resp = 'html'
        result = s and _strip(s.groups() and s.group(1) or s.group()) or ''
        s = parse_search(
            result,
            rule.evalx,
            fields_global=fields_global)
        s = _fmt_json_str(s)
        return yaml.load(s)
    return s and _strip(s.groups() and s.group(1) or s.group()) or None


def _fmt_resp_filter(rule, result):
    if rule.resp == 'json':
        rule._resp = 'html'
        s = parse_search(result, rule.evalx)
        s = _fmt_json_str(s)
        return yaml.load(s)
    return result


def parse_xpath(tree, xpath, fields_global={}):
    result = tree.xpath(format_rule(fields_global, xpath.xpath))
    if not result:
        return None
    result = result[0]
    if xpath.evalx is not None:
        result = eval(xpath.evalx)
        if xpath.resp == 'json':
            return yaml.load(result)
        return result
    if _cls_name(result) == '_ElementStringResult':
        result = _strip(result)
        return _fmt_resp_filter(xpath, result)
    elif _cls_name(result) == '_ElementUnicodeResult':
        result = _strip(_utf8(result))
        return _fmt_resp_filter(xpath, result)
    return _strip(_utf8(result.text))


def parse_xpaths(tree, xpath, fields_global={}):
    results = tree.xpath(format_rule(fields_global, xpath.xpath))
    if not results:
        return None
    if xpath.evalx is not None:
        # 如果节点是 字符类型 则优先
        return [_strip(result)
                if _cls_name(result) == '_ElementStringResult'
                else (
                    _strip(_utf8(result))
                    if _cls_name(result) == '_ElementUnicodeResult'
                    else eval(xpath.evalx)
                )
                for result in results]
    if _cls_name(results[0]) in ('_ElementStringResult', '_Eleuni'):
        results = [_strip(result) for result in results]
        return [_fmt_resp_filter(xpath, result) for result in results]
    elif _cls_name(results[0]) == '_ElementUnicodeResult':
        results = [_strip(_utf8(result)) for result in results]
        return [_fmt_resp_filter(xpath, result) for result in results]
    return [_strip(result.text) for result in results]


def parse_xpathz(field_val, xpathz, fields_global={}):
    if xpathz.xpath.method == 'xpath':
        if isinstance(field_val, list):
            return [parse_xpath(t, xpathz.xpath, fields_global=fields_global) for t in field_val]
        else:
            return parse_xpath(field_val, xpathz.xpath, fields_global=fields_global)
    elif xpathz.xpath.method == 'xpaths':
        if isinstance(field_val, list):
            return [parse_xpaths(t, xpathz.xpath, fields_global=fields_global) for t in field_val]
        else:
            return parse_xpath(field_val, xpathz.xpath, fields_global=fields_global)


def parse_dpath(j, rule, fields_global={}):
    obj = 'j{}'.format(format_rule(fields_global, rule.path))
    result = eval(obj)
    if rule.evalx:
        result = eval(rule.evalx)
    return _utf8(result) if isinstance(result, unicode) else result


class Parser(object):

    def __init__(self, html, rules, encoding='utf-8'):
        """
        @param html :   unicode 文本
        @param rules:   规则列表 {'result_rules': {}}
        @param encoding(optional):  页面编码
        """
        self._html = html
        self._rules = copy.deepcopy(rules)
        self._default_encoding = encoding

        self._tree = None

        self.fields_vals = {}
        self.fields_base = {}
        self.fields_addon = {}
        self.fields_global = {}
        self.fields_ajax_urls = {}
        self.fields_results = {}
        self.html_ajax = {}

    @property
    def tree(self):
        while self._tree is None:
            self._tree = gen_tree(self._html)
        return self._tree

    @property
    def html(self):
        return self._html

    def _url_join(self, url, **params):
        """update url query params

        @param url :    url with query string
        @param params : query params, del param if val is None
        """
        url_obj = list(urlparse(url))
        query = dict(parse_qsl(url_obj[4]))
        for k, v in params.items():
            if v is not None:
                query[k] = quote(v) if isinstance(v, (unicode, basestring, str)) else v
            else:
                if query.has_key(k):
                    query.pop(k)
        url_obj[4] = unquote(urlencode(query))
        return urlunparse(url_obj).decode(self._default_encoding).encode('utf-8')

    def _fmt_encoding(self, encoding):
        if not encoding:
            return self._default_encoding
        if encoding.lower() in ('gbk', 'gb2312'):
            return 'GB18030'
        return encoding

    def parse_base(self, key):
        return self.fields_base[key]

    def parse_addon(self, key):
        return self.fields_addon[key]

    def parse_template(self, html, tree, rule):
        if rule.rule.method == 'xpath':
            return parse_xpath(tree, rule.rule, fields_global=self.fields_global)
        elif rule.rule.method == 'search':
            return parse_search(html, rule.rule, fields_global=self.fields_global)
        else:
            raise Exception('unknow template rule')

    def parse_fields(self, html, tree, field_key, rule):
        if self.fields_vals.get(field_key, None) is not None:
            field_val = self.fields_vals.get(field_key)
        else:
            self.parse_field_rule(field_key)
            field_val = self.fields_vals[field_key]
        if rule is None:
            return field_val
        if rule.method == 'xpath':
            return parse_xpath(gen_tree(field_val), rule, fields_global=self.fields_global)
        elif rule.method == 'search':
            return parse_search(field_val, rule, fields_global=self.fields_global)
        elif rule.method == 'dpath':
            return parse_dpath(field_val, rule, fields_global=self.fields_global)
        elif rule.method == 'xpaths':
            return parse_xpaths(tree, rule, fields_global=self.fields_global)

    def parse_which(self, html, tree, rule):
        for z_rule in rule.rules:
            result = self.parse_all_types(html, tree, None, z_rule)
            if result is not None:
                return result
        return None

    def parse_next(self, html, tree, rule):
        result = None
        while 1:
            z_rule = None
            try:
                z_rule = rule.next_rule.next()
            except StopIteration:
                break
            if z_rule.method == 'xpath':
                result = tree if result is None else result
                result = parse_xpath(result, z_rule)
                if not result:
                    raise Exception('failed to parse next %s' % z_rule.xpath)
            elif z_rule.method == 'search':
                result = html if result is None else result
                result = parse_search(result, z_rule)
                if not result:
                    raise Exception('failed to parse next %s' % z_rule.regx)
        return result

    def parse_all_types(self, html, tree, key, rule):
        if isinstance(rule, (list, tuple)):
            return [self.parse_all_types(html, tree, key, z_rule) for z_rule in rule]
        if not hasattr(rule, 'method'):
            return rule
        if rule.method == 'search':
            return parse_search(html, rule, fields_global=self.fields_global)
        elif rule.method == 'xpath':
            return parse_xpath(tree, rule, fields_global=self.fields_global)
        elif rule.method == 'xpaths':
            return parse_xpaths(tree, rule, fields_global=self.fields_global)
        elif rule.method == 'xpathz':
            if self.fields_vals.get(rule.key, None) is not None:
                field_val = self.fields_vals.get(rule.key)
            else:
                self.parse_field_rule(rule.key)
                field_val = self.fields_vals[rule.key]
            return parse_xpathz(field_val, rule, fields_global=self.fields_global)
        elif rule.method == 'base':
            return self.parse_base(rule.key)
        elif rule.method == 'addon':
            return self.parse_addon(rule.key)
        elif rule.method == 'template':
            return self.parse_template(html, tree, rule)
        elif rule.method == 'next':
            return self.parse_next(html, tree, rule)
        elif rule.method == 'fields':
            return self.parse_fields(html, tree, rule.field_key, rule.rule)
        elif rule.method == 'which':
            return self.parse_which(html, tree, rule)
        elif rule.method == 'ajax':
            _keys = get_format_keys(self.fields_global, repr(rule))
            return {
                'url': self.fields_ajax_urls[rule.api]['url'].decode('utf-8'),
                'rules': {
                    'source': 'ajax',
                    'resp': self.fields_ajax_urls[rule.api]['resp'],
                    'evalx': repr(self.fields_ajax_urls[rule.api]['evalx']),
                    'kwargs': dict((k, self.fields_global[k]) for k in _keys),
                    'field': repr(rule.rule),
                },
            }
        else:
            raise Exception('unknow rule method on %s' % key)

    def parse_all_base(self):
        """parse base_fields keys in rules"""
        for key, rule in self._rules.get('base_fields', {}).items():
            if rule is None:
                continue
            result = None
            try:
                result = self.parse_all_types(self._html, self.tree, key, rule)
            except:
                raise FieldParseError('failed to parse field %s' % key)
            finally:
                if result is None:
                    raise FieldParseError('failed to parse base field %s with rule %s' % (key, rule))
            self.fields_base[key] = result
            self.fields_global[key] = result

    def parse_addon_fields(self):
        for key, rule in self._rules['addon_fields'].items():
            logging.info('start to parse addon field %s' % key)
            if rule is None:
                continue
            try:
                result = self.parse_all_types(self._html, self.tree, key, rule)
            except:
                logging.error(traceback.format_exc())
                raise FieldParseError
                logging.warning('failed to parse addon field %s with rule %s' % (key, rule))
            self.fields_addon[key] = result
            self.fields_global[key] = result

    def parse_field_rule(self, field_key):
        """parse fields_rules with field_key"""
        # for key, rule in self._rules['fields_rules'].items():
        key = field_key
        rule = self._rules['fields_rules'][key]
        result = None
        if rule.method == 'xpath':
            result = parse_xpath(self.tree, rule, fields_global=self.fields_global)
        elif rule.method == 'search':
            result = parse_search(self._html, rule, fields_global=self.fields_global)
        elif rule.method == 'xpaths':
            result = parse_xpaths(self.tree, rule, fields_global=self.fields_global)
        else:
            raise Exception('unexcept fields_rules match type %s' % field_key)
        self.fields_vals[key] = result
        logging.debug('key {} rule {} value {}'.format(key, rule, result))

    def parse_ajax_urls(self):
        """generate ajax url in ajax_rules"""
        for key, ajax in self._rules['ajax_rules'].items():
            host, kwargs = ajax.host, ajax.kwargs
            logging.info('star to parse ajax url of %s' % key)
            # host
            try:
                if not isinstance(host, (str, unicode)):
                    host = self.parse_all_types(self._html, self.tree, key, host)
                # kwargs
                for k, v in kwargs.items():
                    if not isinstance(v, (str, unicode)):
                        kwargs[k] = self.parse_all_types(self._html, self.tree, k, v)
                # join
                url = host and self._url_join(host, **kwargs) or None
                self.fields_ajax_urls[key] = {
                    'url': url,
                    'resp': ajax.resp,
                    'evalx': ajax.evalx}
            except:
                # raise FieldParseError
                logging.warning('failed to parse ajax url of %s' % key)

    def parse_results(self, requires):
        """parse k-v result in result_rules"""
        for key, rule in self._rules['result_rules'].items():
            if rule is None:
                continue
            result = None
            try:
                result = self.parse_all_types(self._html, self.tree, key, rule)
                result = self.parse_result_filter(key, result)
                self.fields_results[key] = result
            except:
                result = None
                logging.warning('failed to parse result of %s' % key)
                logging.debug(traceback.format_exc())
            finally:
                if result is None and key in requires:
                    raise FieldParseError('failed to parse field %s' % key)
            yield key, result

    def parse_result_filter(self, key, result):
        filter_rule = self._rules.get('result_filters', {}).get(key, None)
        if filter_rule is not None:
            func, args = filter_rule
            args = eval(repr(args).format(result=result))
            if func is not None:
                result = eval(func)(*args)
            else:
                result = eval(args)
        return result

    def switch_template(self):
        if self._rules.get('template_rules'):
            for template_id, rules in self._rules['template_rules'].items():
                for rule in rules:
                    try:
                        if parse_search(self._html, rule, fields_global=self.fields_global) is None:
                            break
                    except:
                        raise TemplateParseError
                else:
                    logging.info('switch to template %s' % template_id)
                    self._rules.update(self._rules['template_target'][template_id])
                    break
            else:
                raise TemplateNotFoundError

    def verify_page(self):
        for rule in self._rules.get('page_rules') or []:
            logging.info('start to verify page rules')
            try:
                if self.parse_all_types(self._html, self.tree, None, rule) is None:
                    raise
            except:
                logging.debug(traceback.format_exc())
                raise InvalidPageError

    def parse(self, *fields):
        self.verify_page()
        self.switch_template()
        if self._rules.get('base_fields'):
            self.parse_all_base()
        if self._rules.get('addon_fields'):
            self.parse_addon_fields()
        if self._rules.get('ajax_rules'):
            self.parse_ajax_urls()
        fields = list(fields)
        fields.extend(self._rules.get('base_fields', {}).keys())
        results = list(self.parse_results(requires=list(set(fields))))
        return results

    def __call__(self):
        return self.parse()


class AjaxParser(object):

    def __init__(self, html, rule):
        """
        @rule {
            'source': 'ajax',
            'resp': 'html/json',
            'evalx': search(r''),
            'kwargs': {},
            'field': dpath("['key']"),
        }
        """
        self._html = html
        self._rule = rule
        if rule.get('source') != 'ajax':
            raise Exception('unexcept param rule')
        self._resp = self._rule.get('resp') or 'html'
        self._evalx = self._rule.get('evalx') or None
        self._kwargs = self._rule.get('kwargs') or {}
        self._field = eval(self._rule['field'])

        self._j = None

    def parse_resp(self):
        if self._resp == 'json':
            self._j = parse_search(
                self._html,
                eval(self._evalx.replace('result', 'self._html')),
                self._kwargs)
            self._j = _fmt_json_str(self._j)
            self._j = yaml.load(self._j)

    def parse(self):
        self.parse_resp()

        if self._field.method == 'search':
            return parse_search(self._html, self._field, self._kwargs)
        elif self._field.method == 'dpath':
            return parse_dpath(self._j, self._field, self._kwargs)
        else:
            raise Exception('unsupport field match type %s' % self._field.method)
