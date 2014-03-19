# encoding: utf8
"""
copy from tornado.escape.xhtml_unescape
"""
import re
import htmlentitydefs

if type('') is not type(b''):
    def u(s):
        return s
    bytes_type = bytes
    unicode_type = str
    basestring_type = str
else:
    def u(s):
        return s.decode('unicode_escape')
    bytes_type = str
    unicode_type = unicode
    basestring_type = basestring


def _build_unicode_map():
    unicode_map = {}
    for name, value in htmlentitydefs.name2codepoint.items():
        unicode_map[name] = unichr(value)
    return unicode_map

_HTML_UNICODE_MAP = _build_unicode_map()
_TO_UNICODE_TYPES = (unicode_type, type(None))


def _convert_entity(m):
    if m.group(1) == "#":
        try:
            return unichr(int(m.group(2)))
        except ValueError:
            return "&#%s;" % m.group(2)
    try:
        return _HTML_UNICODE_MAP[m.group(2)]
    except KeyError:
        return "&%s;" % m.group(2)


def to_unicode(value):
    """Converts a string argument to a unicode string.

    If the argument is already a unicode string or None, it is returned
    unchanged.  Otherwise it must be a byte string and is decoded as utf8.
    """
    if isinstance(value, _TO_UNICODE_TYPES):
        return value
    if not isinstance(value, bytes_type):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value)
        )
    return value.decode("utf-8")

_unicode = to_unicode


def xhtml_unescape(value):
    """Un-escapes an XML-escaped string."""
    return re.sub(r"&(#?)(\w+?);", _convert_entity, _unicode(value))
