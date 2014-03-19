# -*- coding: utf-8 -*-
# coding: utf-8


class InvalidPageError(BaseException):
    pass


class TemplateParseError(BaseException):
    pass


class TemplateNotFoundError(BaseException):
    pass


class FieldParseError(BaseException):
    pass


class InvalidFieldError(BaseException):
    pass


class InvalidRuleError(BaseException):
    pass
