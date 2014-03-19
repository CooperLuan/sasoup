# dbotx

重写爬虫

## 需求

1. 分离 HTTP 请求和数据解析
2. 提供淘宝爬虫接口
3. 整合其他爬虫接口
4. 统一错误处理

## 规范

1. 通过 rules 类配置爬虫

## 模块

1. exceptions

   1. InvalidPageError       页面异常
   2. TemplateParseError     模板判断异常
   3. TemplateNotFoundError  未知模板异常
   4. FieldParseError        字段匹配异常
   5. InvalidFieldError      字段非法异常
2. toprules

   1. `url_fmt`             基础 URL 格式 用于构造页面 URL
   2. `page_rules`          验证页面是否合法
   3. `template_rules`      模板判断规则
   4. `fields_rules`        非结果字段匹配规则(可选匹配) 用于构造 ajax 请求
   5. `ajax_rules`          ajax 数据获取规则
   6. `result_rules`        返回字段匹配规则
3. basebot

   1. BaseBot.parse 按照 toprules 中的规则匹配字段
   2. TopBot.flag_deny
   3. WeiboBot.flag_deny
4. topitem

   1. get_basic
   2. get_full
5. ...

## 规则编写

1. 基础结构

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
2. 从 `result_rules` 开始

   允许 `xpath/search` 两种基本匹配方式 和 `which` 复合类型

   ```
   rules = {
       'result_rules': {},
   }
   ```

   匹配结果为 `tuple/list/str` 中的一种
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
