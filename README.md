# sasoup

`sasoup` is a html parser base on `xpath`/`re`

## requirement

  ```sh
  pip install pyyaml
  pip install lxml
  ```

## example

```python
import requests
from sasoup import Parser
from sasoup.baserules import xpath, xpaths, xpathz, search, dpath, base, addon, fields, which
hacker_news = {
    'fields_rules': {
        'news': xpaths("//body/center/table/tr", evalx="result"),
    },
    'result_rules': {
        'title': xpath("//span[@class='pagetop']/b/a"),
        'google': search(r'\>(Google.+?)\<'),
        'html5': search(r'\>(HTML5.+?)\<'),
        'facebook': xpath("//a[contains(text(),'Facebook')]"),
        'titles': xpathz(
            'news',
            xpaths(".//td[@class='title']/a")),
        'tsmps': xpathz(
            'news',
            xpaths(".//td[@class='subtext']/node()[4]")),
        'points': xpathz(
            'news',
            xpaths(".//td[@class='subtext']/span")),
    },
    'result_filters': {
        'titles': (None, "result[2]"),
        'tsmps': (None, "result[2]"),
        'points': (None, "result[2]"),
    }
}

url = 'https://news.ycombinator.com/'
html = requests.get(url).content.decode('utf-8')
results = dict(Parser(html, hacker_news).parse())
for key, result in results.items():
    print '{} : {}'.format(key, result)
```

output

```
google : Google Announces Massive Price Drops for Cloud Computing Services, Storage
tsmps : ['5 hours ago  |', '3 hours ago  |', '3 hours ago  |', '1 hour ago  |', '5 hours ago  |', '10 hours ago  |', '1 hour ago  |', '9 hours ago  |', '4 hours ago  |', '32 minutes ago  |', '8 hours ago  |', '7 hours ago  |', '13 hours ago  |', '12 hours ago  |', '5 hours ago  |', '7 hours ago  |', '7 hours ago  |', '11 hours ago  |', '6 hours ago  |', '10 hours ago  |', '17 minutes ago  |', '3 hours ago  |', '10 hours ago  |', '10 hours ago  |', '10 hours ago  |', '6 hours ago  |', '10 hours ago  |', '9 hours ago  |', '5 hours ago  |']
title : Hacker News
titles : ['Facebook acquires Oculus VR', u'Minecraft creator says he\u2019s canceled talks for Oculus Rift version', 'Virtual Reality is going to change the world', 'Aug. 1, 2012: When Oculus Asked for Donations', 'Oculus Joins Facebook', 'Microsoft makes source code for MS-DOS and Word for Windows available to public', 'Go In Action', 'Google Announces Massive Price Drops for Cloud Computing Services, Storage', "Mistakes we've made", "Mozilla's low-overhead open source replay debugger", 'IRS Says Bitcoin Is Property', u'Show HN: HTML5 clone of OS X AirDrop \u2013 Easy P2P file transfers in a browser', u'We\u2019re Fucked, It\u2019s Over: Coming Back from the Brink', 'Clojure 1.6 released', 'The Future of Virtual Reality', 'Startups, Role Models, Risk, and Y Combinator', 'Fourier transform for dummies', 'Introductions to advanced Haskell topics', 'Nvidia Unveils First Mobile Supercomputer for Embedded Systems', 'Projects that power GitHub', 'Full Disclosure Mailing List: A Fresh Start', u'Facebook\u2019s $2B Oculus deal happened over the last five days', 'Waze Co-Founder Skips Google to Try Startup World Again', u'Game Programming Patterns \u2013 Bytecode', 'Google Cloud Platform Live', 'Spyware app turns the privacy tables on Google Glass wearers', 'Firefox OS: Tracking reflows and event loop lags', 'Clever (YC S12) Confirms $10.3M Raise From Sequoia, Paul Graham', 'Rescale (YC W12) is looking for platform software engineers', "Facebook's Privacy Dinosaur Wants to Make Sure You're Not Oversharing", 'More']
facebook : Facebook acquires Oculus VR
html5 : None
points : ['870 points', '376 points', '225 points', '56 points', '204 points', '596 points', '25 points', '286 points', '76 points', '7 points', '283 points', '98 points', '289 points', '253 points', '43 points', '83 points', '74 points', '137 points', '52 points', '116 points', '3 points', '40 points', '85 points', '78 points', '70 points', '30 points', '68 points', '55 points', '24 points']
```

## how to write rules

1. full rules type

   ```python
   rules = {
       'super': None,           # 继承对象
       'page_rules': (),        # 页面规则
       'template_rules': {},    # 模板规则
       'template_target': {},   # 模板选择
       'fields_rules': {},      # block 段
       'base_fields': {},       # 基础字段
       'addon_fields': {},      # 额外字段
       'ajax_rules': {},        # ajax 组装规则
       'result_rules': {},      # 目标字段匹配规则
       'result_filters': {},    # 字段匹配结果处理
   }
   ```
2. start with `result_rules`

   basic match type `xpath/search` and complex match type `which` is allowed

   ```python
   rules = {
       'result_rules': {},
   }
   ```

3. 如果 `result_rules` 中引用了多个同区域的代码块，则将共同的代码块加入 `fields_rules`

   `fields_rules` 对应的结果可以是 `html/json`

   `result_rules` 增加 `fields/xpathz/dpath` 匹配方式

   ```python
   rules = {
       'fields_rules': {},
       'result_rules': {},
   }
   ```
4. 如果目标页面有多个不同的模板，则将公共字段加入 `base_fields` 区别字段加入 `addon_fields`

   `result_rules` 增加 `base/addon` 匹配方式

   ```python
   rules = {
       'super': base,
       'template_rules': {},
       'template_target': {},
       'base_fields': {},
       'addon_fields': {},
       'result_rules': {},
   }
   ```
5. 如果目标字段在 ajax 请求的返回结果中，则将 url 组成规则加入 `ajax_rules`

   `result_rules` 增加 `ajax` 匹配方式
6. 如果需要对目标字段的匹配结果进一步处理，则添加到 `result_filters`

   可添加 `eval` 参数进行处理

## TODO

1. verify rules
