# encoding: utf8
"""
basic match

    xpath           etree.xpath
        RespType    html/json
        evalx       exec eval to result
    xpaths
        RespType    html/json
        evals       eval obj
    xpathz
        xpath
    search          re.search
        RespType    html/json
        evalx       expression to extract json string 
    dpath           dict['key'] || eval code

complex match

    base            get from base_fields
    addon           get from addon_fields 按需匹配
    next(*args)     从上一个参数的匹配结果中匹配
    template        按照模板匹配
    fields          从 fields_rules 的结果中匹配
    which           逐一匹配直到有结果
    ajaxurl         ajax 请求参数
        resp_type   html/json
        resp_filter regx expression to extract json string
    ajax            从 ajax 请求结果中匹配 按需请求

"""


def enum(name, *sequential, **named):
    values = dict(zip(sequential, range(len(sequential))), **named)
    return type(name, (), values)

RespType = enum('RespType', HTML='html', JSON='json')


class MatchType(object):

    def __init__(self):
        self._method = self.__class__.__name__

    @property
    def method(self):
        return self._method

    def __repr__(self):
        return self.__str__()


class xpath(MatchType):

    def __init__(self, exp, resp=RespType.HTML, evalx=None):
        """
        @param resp :   html/json
        @param evals :  eval(obj) or search obj
        """
        super(xpath, self).__init__()
        self._xpath = exp
        self._resp = resp
        self._evalx = evalx
        assert self._resp in ('html', 'json')

    @property
    def xpath(self):
        return self._xpath

    @property
    def resp(self):
        return self._resp

    @property
    def evalx(self):
        return self._evalx

    def __str__(self):
        return 'xpath["%s"]' % self._xpath


class xpaths(MatchType):

    def __init__(self, exp, resp=RespType.HTML, evalx=None):
        super(xpaths, self).__init__()
        self._xpath = exp
        self._resp = resp
        self._evalx = evalx

    @property
    def xpath(self):
        return self._xpath

    @property
    def resp(self):
        return self._resp

    @property
    def evalx(self):
        return self._evalx

    def __str__(self):
        return 'xpath["%s"]' % self._xpath


class xpathz(MatchType):

    def __init__(self, key, xpath):
        super(xpathz, self).__init__()
        self._key = key
        self._xpath = xpath

    @property
    def key(self):
        return self._key

    @property
    def xpath(self):
        return self._xpath

    def __str__(self):
        return 'xpathz["%s", xpath]' % (self._key, self._xpath)


class search(MatchType):

    def __init__(self, rule, resp=RespType.HTML, evalx=None):
        super(search, self).__init__()
        self._rule = rule
        self._resp = resp
        self._evalx = evalx

    @property
    def regx(self):
        return self._rule

    @property
    def resp(self):
        return self._resp

    @property
    def evalx(self):
        return self._evalx

    def __str__(self):
        return "search(r'%s', resp='%s', evalx='%s')" % (
            self._rule,
            self._resp,
            self._evalx or 'result')


class dpath(MatchType):

    def __init__(self, rule, evalx=None):
        super(dpath, self).__init__()
        self._rule = rule
        self._evalx = evalx

    @property
    def path(self):
        return self._rule

    @property
    def evalx(self):
        return self._evalx

    def __str__(self):
        return 'dpath("%s", evalx="%s")' % (self._rule, self._evalx or 'result')


class base(MatchType):

    def __init__(self, key):
        super(base, self).__init__()
        self._key = key

    @property
    def key(self):
        return self._key

    def __str__(self):
        return 'base[%s]' % self._key


class addon(MatchType):

    def __init__(self, key):
        super(addon, self).__init__()
        self._key = key

    @property
    def key(self):
        return self._key

    def __str__(self):
        return 'addon[%s]' % self._key


class next(MatchType):

    def __init__(self, *args):
        super(next, self).__init__()
        self._rules = list(args)
        self.__sorted = list(reversed(self._rules))

    @property
    def next_rule(self):
        try:
            yield self.__sorted.pop()
        except IndexError:
            return

    def __str__(self):
        return 'next[%s]' % ', '.join([str(rule) for rule in self._rules])


class template(MatchType):

    def __init__(self, template_id, rule):
        super(template, self).__init__()
        self._template_id = template_id
        self._rule = rule

    @property
    def id(self):
        return self._template_id

    @property
    def rule(self):
        return self._rule

    def __str__(self):
        return 'template[%s, %s]' % (self._template_id, self._rule)


class fields(MatchType):

    def __init__(self, field_key, rule=None):
        super(fields, self).__init__()
        self._field_key = field_key
        self._rule = rule

    @property
    def field_key(self):
        return self._field_key

    @property
    def rule(self):
        return self._rule

    def __str__(self):
        return 'fields[%s, %s]' % (self._field_key, self._rule)


class which(MatchType):

    def __init__(self, *args):
        super(which, self).__init__()
        self._rules = list(args)
        self.__sorted = list(reversed(self._rules))

    @property
    def next_rule(self):
        try:
            yield self.__sorted.pop()
        except IndexError:
            return

    @property
    def rules(self):
        return self._rules

    def __str__(self):
        return 'which[%s]' % ', '.join([str(rule) for rule in self._rules])


class ajaxurl(MatchType):

    def __init__(self, host, resp=RespType.HTML, evalx=None, **kwargs):
        super(ajaxurl, self).__init__()
        self._host = host
        self._resp = resp
        self._evalx = evalx
        self._kwargs = kwargs

    @property
    def host(self):
        return self._host

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def resp(self):
        return self._resp

    @property
    def evalx(self):
        return self._evalx

    def __str__(self):
        return 'ajaxurl(%s, "%s", "%s", **%s)' % (
            self._host, self._resp,
            self._evalx, self._kwargs)


class ajax(MatchType):

    def __init__(self, api, rule):
        super(ajax, self).__init__()
        self._api = api
        self._rule = rule

    @property
    def api(self):
        return self._api

    @property
    def rule(self):
        return self._rule

    def __str__(self):
        return "ajax('%s', %s)" % (self._api, self._rule)


def init_rules(rules):
    """处理 rules 的继承关系
    @param rules :  顶层 rules
    @return :       合并 super 规则后的 rules
    """
    # get super object
    super_obj = rules.get('super', None) is not None and rules.pop('super') or None
    if super_obj is not None:
        # init super object
        super_obj = init_rules(super_obj)
        # update from super unexisted k-v pairs
        for key in super_obj.keys():
            if rules.get(key, None) is None:
                rules[key] = super_obj.get(key, None)
        # update dict/tuple/list values
        for key, rule in rules.items():
            if isinstance(rule, (tuple, list)):
                rules[key] = list(super_obj.get(key, ())) + list(rule)
            elif isinstance(rule, dict):
                sr = super_obj.get(key, dict()).copy()
                sr.update(rules[key])
                rules[key] = sr
    return rules
