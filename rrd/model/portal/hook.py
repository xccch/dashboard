# -*- coding:utf-8 -*-
# Copyright 2017 Xiaomi, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'Zongqing.liu'
from .bean import Bean


class Hook(Bean):
    _tbl = 'hook'
    _cols = 'id,strategy_id,expression_id,when_status,when_step,hook_method,hook_url,params'

    def __init__(self, _id, strategy_id, expression_id, when_status, when_step, hook_method, hook_url, params):
        self.id = _id
        self.strategy_id = strategy_id
        self.expression_id = expression_id
        self.when_status = when_status
        self.when_step = when_step
        self.hook_method = hook_method
        self.hook_url = hook_url
        self.params = params

    def to_json(self):
        return {
            'id': self.id,
            'strategy_id': self.strategy_id,
            'expression_id': self.expression_id,
            'when_status': self.when_status,
            'when_step': self.when_step,
            'hook_method': self.hook_method,
            'hook_url': self.hook_url,
            'params': self.params
        }

