# coding: utf-8


class InvalidPageError(Exception):
    pass


class TemplateParseError(Exception):
    pass


class TemplateNotFoundError(Exception):
    pass


class FieldParseError(Exception):
    pass


class InvalidFieldError(Exception):
    pass


class InvalidRuleError(Exception):
    pass
