# encoding: utf8
from sasoup.baserules import xpath, xpaths, xpathz, search, dpath, base, addon, fields, which, next, ajaxurl, ajax, RespType
from sasoup.baserules import init_rules

rules = {
    'url': 'http://www.etao.com',
    'fields_rules': {
        'feedList': xpaths("//div[@id='J_FeedList']//div[@id]", evalx="result"),
    },
    'result_rules': {
        'feed': (
            xpathz('feedList', xpath(".//h3[@class='feed-title']/a/@title", evalx="_strip(result)")),
            xpathz('feedList', xpath(".//h3[@class='feed-title']/a/strong/text()", evalx="_strip(result)")),
            xpathz('feedList', xpath(".//div[@class='feed-desc']/p/text()", evalx="_strip(result)")),
        ),
        'cats': next(
            xpaths("//div[contains(@class,'J_PCMain')/li]", evalx="result"),
            xpath(".//h3/a/text()", evalx="result"),
        ),
    },
}

rules = init_rules(rules)
