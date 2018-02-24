# -*- coding:utf-8 -*-

__author__ = 'Zongqing.liu'
from .bean import Bean


class Tag(Bean):
    _tbl = 'tags'
    _id = 'id'
    _cols = 'id, name'

    def __init__(self, _id, name):
        self.id = _id
        self.name = name