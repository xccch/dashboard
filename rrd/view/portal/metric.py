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

from rrd import app
from flask import render_template, request, g, jsonify
from rrd.model.portal.metric import Metric

from rrd.utils.logger import logging

log = logging.getLogger(__file__)


@app.route('/portal/metric', methods=["GET", ])
def metric_get():
    page = int(request.args.get('p', 1))
    limit = int(request.args.get('limit', 50))
    query = request.args.get('q', '').strip()
    vs, total = Metric.query(page, limit, query)
    log.debug(vs)
    return render_template(
        'portal/metric/index.html',
        data={
            'vs': vs,
            'total': total,
            'query': query,
            'limit': limit,
            'page': page
        }
    )


@app.route('/portal/metric/delete/<metric_id>')
def metric_delete_get(metric_id):
    metric_id = int(metric_id)
    t = Metric.get(metric_id)
    if not t:
        return jsonify(msg='no such metric')

    Metric.delete_one(metric_id)
    return jsonify(msg='')


