# encoding: utf8
from sasoup.baserules import xpath, xpaths, xpathz, search, dpath, base, addon, fields, which, ajaxurl, ajax, RespType

appsorules = {
    'fields_rules': {
        'items': xpaths("//div[contains(@id, 'liveblog-entry-')]/div", evalx="result"),
    },
    'result_rules': {
        'tsmp': xpathz(
            'items',
            xpaths(".//p[1]/strong", evalx="result.text")),
        'title': xpathz(
            'items',
            xpaths(".//p[2]/a/strong", evalx="result.text")),
        'link': xpathz(
            'items',
            xpaths(".//p[2]/a/@href")),
        'desc': xpathz(
            'items',
            xpaths(".//p[3]", evalx="result.text")),
        'intro': xpathz(
            'items',
            xpaths(".//p[4]", evalx="result.text")),
    },
}
