# sasoup change list

# v0.2.1

1. add property `rules` to match type `which`
2. fix `Parser.parse_which` bug
3. update base class of exception from `BaseException` to `Exception`, as `BaseException` result to exit of celery worker

# v0.2

1. add `verify_page` to Parser, base on `page_rules`, if exists
2. add `exceptions.*` to `parser`, make error readable to user
