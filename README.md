# sasoup

`sasoup` is a html parser base on `xpath`/`re`

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
