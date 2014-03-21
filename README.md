# sasoup

`sasoup` is a html parser base on `xpath`/`re`

## requirement

  ```sh
  pip install pyyaml
  pip install lxml
  ```

## example

```
import requests
from sasoup import Parser
from sasoup.baserules import xpath, xpaths, xpathz, search, dpath, base, addon, fields, which
hacker_news = {
    'fields_rules': {
        'news': xpaths("//body/center/table/tr", evalx="result"),
    },
    'result_rules': {
        'title': xpath("//span[@class='pagetop']/b/a"),
        'django': search(r'\>(Django.+?)\<'),
        'twitter': search(r'\>(Twitter.+?)\<'),
        'elastic': xpath("//a[contains(text(),'Elasticsearch')]"),
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

## how to write rules

1. full rules type

   ```
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

   ```
   rules = {
       'result_rules': {},
   }
   ```

3. 如果 `result_rules` 中引用了多个同区域的代码块，则将共同的代码块加入 `fields_rules`

   `fields_rules` 对应的结果可以是 `html/json`

   `result_rules` 增加 `fields/xpathz/dpath` 匹配方式

   ```
   rules = {
       'fields_rules': {},
       'result_rules': {},
   }
   ```
4. 如果目标页面有多个不同的模板，则将公共字段加入 `base_fields` 区别字段加入 `addon_fields`

   `result_rules` 增加 `base/addon` 匹配方式

   ```
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
