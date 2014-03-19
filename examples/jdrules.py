# encoding: utf8
from sasoup.baserules import xpath, xpaths, xpathz, search, dpath, base, addon, fields, which, ajaxurl, ajax, RespType

"""
jdrules:
    cat:                顶级类目
    electrontics_cat:   家电通讯类目列表
    electrontics_items: 家电通讯类目特价商品
    digitals_cat:       电脑数码类目列表
    digitals_items:     电脑数码类目特价商品
"""
jdrules = {
    'fields_rules': {
        'catItems': xpaths("//div[@id='_JD_ALLSORT']/div", evalx="result"),
        'cat1Cats': xpaths("//div[@id='electronics']/div[contains(@class,'catalogue')]//ul/li", evalx="result"),
        'cat1Items': xpaths("//div[@id='electronics']/div[contains(@class,'plist')]/div[2]//li", evalx="result"),
        'cat2Cats': xpaths("//div[@id='digitals']/div[contains(@class,'catalogue')]//ul/li", evalx="result"),
        'cat2Items': xpaths("//div[@id='digitals']/div[contains(@class,'plist')]/div[2]//li", evalx="result"),
    },
    'result_rules': {
        'cat': xpathz(
            'catItems',
            xpaths(".//h3/a", evalx="result.text")),
        'electrontics_cat': xpathz(
            'cat1Cats',
            xpath(".//a", evalx="result.text")),
        'electrontics_items': xpathz(
            'cat1Items',
            xpaths("./div[@class='p-name']/a|./div[@class='p-price']/span", evalx="result.text")),
        'digitals_cat': xpathz(
            'cat2Cats',
            xpath(".//a", evalx="result.text")),
        'digitals_items': xpathz(
            'cat2Items',
            xpaths("./div[@class='p-name']/a|./div[@class='p-price']/node()", evalx="result.text")),
    },
}
