# -*- coding: utf-8 -*-
# coding: utf-8
"""
template_rules :    模板 ID 判断规则
fields_rules :      非必要字段匹配规则
base_fields :       页面基础字段
ajax_rules :        页面 ajax URL 构造规则
result_rules :      结果字段匹配规则
result_filters :    进一步处理匹配结果

每个匹配页面是一个 dict 对象，此对象可以继承
"""
import time

from sasoup.baserules import xpath, xpaths, search, dpath, base, addon, fields, which, ajaxurl, ajax, RespType
from sasoup.baserules import init_rules

top_item_base = {
    'super': None,
    'url_fmt': 'http://item.taobao.com/item.htm?id={iid}',
    'page_rules': (
        search(r'siteId=\d'),
        xpath("//div[@id='LineZing']"),
    ),
    'template_rules': {
        'B': (
            search(r'siteId=2'),
        ),
        'C': (
            search(r'siteId=[134567]'),
        ),
    },
    'fields_rules': {
        'microscope-data': xpath("//meta[@name='microscope-data']/@content"),
        'exparams': search(r'\([\'"]exparams[\'"]\,\s*[\'"](.+?)[\'"]'),
        'itemViewed': xpath("//div[@id='J_itemViewed']/@data-value", RespType.JSON),
    },
    'base_fields': {
        'siteId': search(r'siteId=(\d)'),
        'itemId': xpath("//div[@id='LineZing']/@itemid"),
        'shopId': xpath("//div[@id='LineZing']/@shopid"),
        'userId': search(r'userid=(\d+)'),
    },
    'addon_fields': {
        'starts': search(r'starts=(\d+)'),
        'ends': search(r'ends=(\d+)'),
    }
}

top_citem = {
    'super': top_item_base,
    'fields_rules': {
        'sku': search(r'Hub\.config\.set\(\'sku\'(.+?)\)', RespType.JSON, search(r'(\{.+\})')),
        'counterApi': search(r'counterApi:[\'"](.+?)[\'"]'),
        'detailParams': xpath(
            "//button[@id='J_listBuyerOnView']",
            evalx="getattr(result, 'attrib')['data-api']"),
        'reviewsListApi': xpath(
            "//div[@id='reviews']",
            evalx="getattr(result, 'attrib')['data-listapi']"),
    },
    'base_fields': {},
    'addon_fields': {
        'apiItemCollectsKey': fields(
            'sku',
            dpath("['apiItemCollects']", "dict(parse_qsl(list(urlparse(result))[4]))['keys']")),
        'apiItemViewsKey': fields(
            'sku',
            dpath("['apiItemViews']", "dict(parse_qsl(list(urlparse(result))[4]))['keys']")),
    },
    'ajax_rules': {
        'wholeSibUrl': ajaxurl(
            fields('sku', dpath("['wholeSibUrl']")),
            RespType.JSON,
            search(r'postage:(\{.+?\})'),
            prior=1,
            ref=''
        ),
        'saveCounts': ajaxurl(
            fields('counterApi', search(r'')),
            RespType.JSON,
            search(r'(\{.+\})'),
            callback='DT.mods.SKU.CountCenter.saveCounts',
        ),
        'rateCounterApi': ajaxurl(
            search(r'rateCounterApi:[\'"](.+?)[\'"]'),
            RespType.JSON,
            search(r'(\{.+\})'),
            callback='DT.mods.SKU.CountCenter.setReviewCount',
        ),
        'apiItemInfo': ajaxurl(
            fields('sku', dpath("['apiItemInfo']")),
            RespType.JSON,
            search(r'(\{.+\})'),
            callback='DT.mods.SKU.GetItemInfo.fire'
        ),
        'oldDealRecords': ajaxurl(
            fields('detailParams'),
            RespType.JSON,
            search(r'(\{.+\})'),
            step='null',
            bid_page=None,
            bidPage=1,
            old_quantity=0,
            sold_total_num='null',
            is_start='true',
            offer='null',
            closed='false',
            callback='Hub.data._receive',
        ),
        'oldRateList': ajaxurl(
            # 'http://rate.taobao.com/feedRateList.htm?userNumId=122654331&auctionNumId=13687831126&siteID=4',
            fields('reviewsListApi'),
            RespType.JSON,
            search(r'(\{.+\})'),
            currentPageNum=1,
            rateType='',
            orderType='',
            showContent='1',
            attribute='',
            callback='jsonp_reviews_list',
        ),
    },
    'result_rules': {
        'siteId': base('siteId'),
        'itemId': base('itemId'),
        'pageId': which(
            fields('microscope-data', search(r'pageId=(\d+)')),
            search(r'pageId\s*:\s*[\'"](\d+)[\'"]'),
        ),
        'shopId': base('shopId'),
        'userId': base('userId'),
        'shopName': search(r'shopName\s*:\s*[\'"](.+?)[\'"],'),
        'wangWang': which(
            xpath("//span[@class='J_WangWang']", evalx="getattr(result, 'attrib')['data-nick']"),
            search(r'sellerNick\s*:\s*[\'"](.+?)[\'"]'),
            search(r'nickName\s*:\s*[\'"](.+?)[\'"]'),
        ),
        'shopUrl': which(
            xpath("//a[contains(@class, 'seller-name')]/@href"),
            xpath("//a[contains(@class,'enter-shop')]/@href"),
        ),
        'itemImg': xpath("//img[@id='J_ImgBooth']/@data-src"),
        'itemTitle': fields('itemViewed', dpath("['title']")),
        'initPrice': fields('itemViewed', dpath("['price']")),
        'promoInfo': None,
        'postageInfo': None,
        'monthlyTrade': ajax('apiItemInfo', dpath("['quantity']['quanity']")),
        'itemRate': None,
        'bonus': None,
        'favNum': ajax('saveCounts', dpath("['{apiItemCollectsKey}']")),
        'totalSoldOut': None,
        'attrList': xpaths(
            "//ul[@class='attributes-list']/li",
            # evalx="re.split(u'[:\uff1a]', _strip(result.text))",
            evalx="result.text.partition(':' if result.text.partition(':')[0] < result.text.partition(u'\uff1a')[0] else u'\uff1a')[::2]"),
        'reviewCount': ajax('saveCounts', dpath("['{apiItemViewsKey}']")),
        'starts': addon('starts'),
        'ends': addon('ends'),
        'userTag': None,
        'cid': None,
        'location': ajax('wholeSibUrl', dpath("['location']")),
        'brand': None,
        'gradeAvg': None,
        'peopleNum': None,
        'periodSoldQuantity': None,
        'rateTotal': None,
        'spuId': None,
        'totalSoldQuantity': None,
        'offSale': None,
        'quanity': ajax('apiItemInfo', dpath("['quantity']['quanity']")),
        'paySuccess': ajax('apiItemInfo', dpath("['quantity']['paySuccess']")),
        'confirmGoods': ajax('apiItemInfo', dpath("['quantity']['confirmGoods']")),
        'paySuccessItems': ajax('apiItemInfo', dpath("['quantity']['paySuccessItems']")),
        'confirmGoodsItems': ajax('apiItemInfo', dpath("['quantity']['confirmGoodsItems']")),
        'shopRank': xpath("//img[@class='rank']/@src"),
        'shopGoodRate': None,
        'created': None,
        'brandName': None,
        'photoUrl': fields('itemViewed', dpath("['pic']")),
        'dsrUrl': xpath("//a[@id='miniDSR']/@href"),
        'dsrUserId': None,
        'dsrRatelink': which(
            xpath("//a[contains(@class, 'rank-icon')]/@href"),
            xpath("//a[@id='shop-rank']/@href"),
            xpath("//a[@id='miniDSR']/@href"),
            xpath("//a[contains(@class, 'mini-dsr')]/@href"),
        ),
        'sellerId': search(r'sellerId=(\d+)'),
        'whoPayShip': None,
        'rootCatId': search(r'rootCatId=(\d+)'),
        'at_bucketid': None,
        'b2c_brand': None,
        'at_autype': None,
        'bucketId': None,
        'skuPrice': None,
        'brandId': None,
        'categoryId': None,
        'quantity': None,
        'tradeList': ajax('oldDealRecords', dpath("['html']")),
        'skuMap': fields('sku', dpath("['valItemInfo']['skuMap']")),
        'rateList': ajax('oldRateList', dpath("['comments']"))
    },
    'result_filters': {
        'shopName': ('_unescape', (u'{result}', )),
        'wangWang': (None, "unquote(result).encode('utf-8')"),
        'initPrice': (None, '{result}/100.00'),
        'shopRank': (None, "re.search(r'newrank/(.+?)\.gif$', '{result}').group(1)"),
        'attrList': (None, "dict((k, v.strip(u' \xa0')) for k, v in result)"),
    },
}

top_tmallitem = {
    'super': top_item_base,
    'url_fmt': 'http://detail.tmall.com/item.htm?id={iid}',
    'fields_rules': {
        'tshop-config': xpath("//form[@id='J_FrmBid']/following-sibling::script"),
        'detailParams': xpath("//button[@id='J_listBuyerOnView']", evalx="getattr(result, 'attrib')['detail:params']"),
        'TShop.Setup': search(r'TShop\.Setup\((.+?)\)', RespType.JSON, search(r'(\{.+\})'))
    },
    'base_fields': {
        'spuId': fields('tshop-config', search(r'spuId[\'"]\s*:\s*[\'"](\d+)[\'"]')),
        'sellerId': fields('tshop-config', search('sellerId=(\d+)')),
        'userTag': search(r'UserTag=(\d+)'),
    },
    'addon_fields': {
        'favKey': fields('tshop-config', search(r'apiBeans[\'"]\s*:\s*[\'"].+?,(.+?)[\'"]')),
        'totalSQ': fields('detailParams', search(r'totalSQ=(\d+)')),
        'sbn': fields('detailParams', search(r'sbn=([a-z0-9]+)')),
    },
    'ajax_rules': {
        'initApi': ajaxurl(
            fields('tshop-config', search(r'initApi[\'"]\s*:\s*[\'"](.+?)[\'"]')),
            RespType.JSON,
            search(r'(\{.+\})'),
            callback='onMdskip',
            ref='',
            brandSiteId=fields('tshop-config', search(r'brandSiteId[\'"]\s*:\s*[\'"](\d+)[\'"]'))
        ),
        'list_dsr_info': ajaxurl(
            'http://dsr.rate.tmall.com/list_dsr_info.htm',
            RespType.JSON,
            search(r'(\{.+\})'),
            itemId=base('itemId'),
            spuId=base('spuId'),
            sellerId=base('sellerId'),
        ),
        'apiBeans': ajaxurl(
            fields('tshop-config', search(r'apiBeans[\'"]\s*:\s*[\'"](.+?)[\'"]')),
            RespType.JSON,
            search(r'(\{.+\})'),
            callback='jsonp151',
            _ksTS=('%.3f' % (time.time() * 1000)).replace('.', '_')
        ),
        'oldDealRecords': ajaxurl(
            'http://tbskip.taobao.com/json/show_buyer_list.htm',
            RespType.JSON,
            search(r'(\{.+\})'),
            is_offline='',
            page_size='15',
            item_type='b',
            ends=addon('ends'),
            starts=addon('starts'),
            item_id=base('itemId'),
            user_tag=base('userTag'),
            old_quantity='0',
            sold_total_num=0,
            closed='false',
            seller_num_id=base('sellerId'),
            zhichong='true',
            taohua='',
            is_from_detail='yes',
            total_sq=addon('totalSQ'),
            bid_page=1,
            callback='TShop.mods.DealRecord.reload',
            t='%.0f' % (time.time() * 1000),
            page_sizename='pageSize',
            is_start='true',
            title='null',
            sbn=addon('sbn'),
        ),
        'dealRecords': ajaxurl(
            fields('detailParams', search(r'^(.+)$')),
            RespType.JSON,
            search(r'(\{.+\})'),
            _ksTS=('%.3f' % (time.time() * 1000)).replace('.', '_'),
            callback='jsonp1422',
            # sold_total_num='{monthlyTrade}',
        ),
        'oldRateList': ajaxurl(
            'http://rate.tmall.com/list_detail_rate.htm',
            RespType.JSON,
            search(r'(\{.+\})'),
            callback='jsonp%d' % (time.time() * 1000),
            itemId=base('itemId'),
            spuId=base('spuId'),
            sellerId=base('userId'),
            order='1',
            append='0',
            currentPage='1',
            ismore='1',
            forShop='1',
        ),
    },
    'result_rules': {
        'siteId': base('siteId'),
        'itemId': base('itemId'),
        'pageId': fields('microscope-data', search(r'pageId=(\d+)')),
        'shopId': base('shopId'),
        'userId': which(
            base('userId'),
            fields('microscope-data', search(r'userid=(\d+)'))),
        'shopName': which(
            xpath("//a[@class='slogo-shopname']"),
            xpath("//input[@name='seller_nickname']/@value"),
        ),
        'shopUrl': which(
            xpath("//a[@class='slogo-shopname']/@href"),
            xpath("//a[@class='enter-shop']/@href"),
            xpath("//input[@id='J_ShopSearchUrl']/@value"),
        ),
        'itemImg': xpath("//img[@id='J_ImgBooth']/@src"),
        'itemTitle': which(
            xpath("//div[@class='tb-detail-hd']/h3//text()"),
            xpath("//input[@name='title']/@value"),
        ),
        'initPrice': search(r'[\'"]defaultItemPrice[\'"]\s*:\s*[\'"](\s*\d+\.*\d*\s*-*\s*\d*\.*\d*)[\'"]'),
        'promoInfo': None,
        'postageInfo': None,
        'monthlyTrade': ajax('initApi', dpath("['defaultModel']['sellCountDO']['sellCount']")),
        'itemRate': ajax('list_dsr_info', dpath("['dsr']['rateTotal']")),
        'bonus': None,
        'favNum': ajax('apiBeans', dpath("['{favKey}']")),
        'totalSoldOut': None,
        'attrList': xpaths(
            "//ul[@id='J_AttrUL']/li",
            evalx="result.text.partition(':' if result.text.partition(':')[0] < result.text.partition(u'\uff1a')[0] else u'\uff1a')[::2]"),
        'reviewCount': None,
        'starts': addon('starts'),
        'ends': addon('ends'),
        'userTag': base('userTag'),
        'cid': None,
        'location': xpath("//input[@name='region']/@value"),
        'brand': fields('TShop.Setup', dpath("['itemDO']['brand']")),
        'gradeAvg': ajax('list_dsr_info', dpath("['dsr']['gradeAvg']")),
        'peopleNum': None,
        'periodSoldQuantity': None,
        'rateTotal': ajax('list_dsr_info', dpath("['dsr']['rateTotal']")),
        'spuId': fields('TShop.Setup', dpath("['itemDO']['spuId']")),
        'totalSoldQuantity': fields('detailParams', search(r'totalSQ=(\d+)')),
        'offSale': None,
        'quanity': None,
        'paySuccess': None,
        'confirmGoods': None,
        'paySuccessItems': None,
        'confirmGoodsItems': None,
        'shopRank': None,
        'shopGoodRate': None,
        'created': None,
        'brandName': None,
        'photoUrl': xpath("//input[@name='photo_url']/@value"),
        'dsrUrl': xpath("//input[@id='dsr-url']/@value"),
        'dsrUserId': xpath("//input[@id='dsr-userid']/@value"),
        'dsrRatelink': xpath("//input[@id='dsr-ratelink']/@value"),
        'sellerId': xpath("//input[@name='seller_id']/@value"),
        'whoPayShip': xpath("//input[@name='who_pay_ship']/@value"),
        'rootCatId': xpath("//input[@name='rootCatId']/@value"),
        'catagory': fields('exparams', search(r'category\=(.+?)&')),
        'at_bucketid': fields('exparams', search(r'at_bucketid\=(.+?)&')),
        'b2c_brand': fields('exparams', search(r'b2c_brand\=(.+?)&')),
        'at_autype': fields('exparams', search(r'at_autype\=(.+?)&')),
        'bucketId': search(r'bucketId:[\'"](\d+)[\'"]'),
        'skuPrice': ajax('initApi', dpath("['defaultModel']['itemPriceResultDO']['priceInfo']")),
        'brandId': fields('TShop.Setup', dpath("['itemDO']['brandId']")),
        'categoryId': fields('TShop.Setup', dpath("['itemDO']['categoryId']")),
        'quantity': fields('TShop.Setup', dpath("['itemDO']['quantity']")),
        'tradeList': ajax('oldDealRecords', dpath("['html'].encode('utf-8')")),
        'rateList': ajax('oldRateList', dpath("['rateDetail']['rateList']")),
    },
    'result_filters': {
        'catagory': ('unquote', ('{result}', )),
        'at_bucketid': ('unquote', ('{result}', )),
        'at_autype': ('unquote', ('{result}', )),
        'brand': ('_unescape', ('{result}', )),
        'attrList': (None, "dict((k, v.strip(u' \xa0')) for k,v in result)"),
    },
}


top_item = {
    'super': top_item_base,
    'template_target': {
        'B': top_tmallitem,
        'C': top_citem,
    }
}


top_tmallitem = init_rules(top_tmallitem)
top_citem = init_rules(top_citem)
top_item = init_rules(top_item)
