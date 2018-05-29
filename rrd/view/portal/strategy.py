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


__author__ = 'Ulric Qin'
from rrd import app
from flask import request, jsonify
from rrd.model.portal.strategy import Strategy
from rrd.model.portal.hook import Hook


@app.route('/portal/strategy/update', methods=['POST'])
def strategy_update_post():
    sid = request.form['sid'].strip()
    metric = request.form['metric'].strip()
    tags = request.form['tags'].strip()
    max_step = request.form['max_step'].strip()
    priority = request.form['priority'].strip()
    note = request.form['note'].strip()
    func = request.form['func'].strip()
    op = request.form['op'].strip()
    right_value = request.form['right_value'].strip()
    run_begin = request.form['run_begin'].strip()
    run_end = request.form['run_end'].strip()
    tpl_id = request.form['tpl_id'].strip()
    category = request.form['category'].strip()

    if not metric:
        return jsonify(msg='metric is blank')

    if metric == 'net.port.listen' and '=' not in tags:
        return jsonify(msg='if metric is net.port.listen, tags should like port=22')

    if sid:
        # update
        Strategy.update_dict(
            {
                'metric': metric,
                'tags': tags,
                'max_step': max_step,
                'priority': priority,
                'func': func,
                'op': op,
                'right_value': right_value,
                'note': note,
                'run_begin': run_begin,
                'run_end': run_end,
                'category': category
            },
            'id=%s',
            [sid]
        )
        return jsonify(msg='')

    # insert
    Strategy.insert(
        {
            'metric': metric,
            'tags': tags,
            'max_step': max_step,
            'priority': priority,
            'func': func,
            'op': op,
            'right_value': right_value,
            'note': note,
            'run_begin': run_begin,
            'run_end': run_end,
            'tpl_id': tpl_id,
            'category': category
        }
    )
    return jsonify(msg='')


@app.route('/portal/strategy/<sid>')
def strategy_get(sid):
    sid = int(sid)
    s = Strategy.get(sid)
    if not s:
        return jsonify(msg='no such strategy')

    return jsonify(msg='', data=s.to_json())


@app.route('/portal/strategy/delete/<sid>')
def strategy_delete_get(sid):
    sid = int(sid)
    s = Strategy.get(sid)
    if not s:
        return jsonify(msg='no such strategy')

    Hook.delete(where="strategy_id={id}".format(id=sid))
    Strategy.delete_one(sid)

    return jsonify(msg='')


@app.route('/portal/hook/<hid>')
def hook_get(hid):
    hid = int(hid)
    hook = Hook.get(hid)
    if not hook:
        return jsonify(msg='no such hook')

    return jsonify(msg='', data=hook.to_json())


@app.route('/portal/strategy/<sid>/hook')
def strategy_list_hook(sid):
    sid = int(sid)
    s = Strategy.get(sid)
    if not s:
        return jsonify(msg='no such strategy')

    hooks = Hook.select_vs(where="strategy_id={id}".format(id=sid))
    data = []
    for hook in hooks:
        data.append(hook.to_json())
    return jsonify(msg='', data=data)


@app.route('/portal/hook/update', methods=['POST'])
def hook_update_post():
    hid = request.form['hid'].strip()
    sid = request.form['sid'].strip()
    when_status = request.form['when_status'].strip()
    when_step = request.form['when_step'].strip()
    hook_method = request.form['hook_method'].strip()
    hook_url = request.form['hook_url'].strip()
    params = request.form['params'].strip()

    if not when_step or not hook_url:
        return jsonify(msg='when_step or hook_url is blank')

    if hid:
        # update
        Hook.update_dict(
            {
                'when_status': when_status,
                'when_step': when_step,
                'hook_method': hook_method,
                'hook_url': hook_url,
                'params': params
            },
            'id=%s',
            [hid]
        )
        return jsonify(msg='')

    # insert
    Hook.insert(
        {
            'strategy_id': sid,
            'expression_id': 0,
            'when_status': when_status,
            'when_step': when_step,
            'hook_method': hook_method,
            'hook_url': hook_url,
            'params': params
        }
    )
    return jsonify(msg='')


@app.route('/portal/hook/delete/<hid>')
def hook_delete_get(hid):
    hid = int(hid)
    hook = Hook.get(hid)
    if not hook:
        return jsonify(msg='no such hook')

    Hook.delete_one(hid)

    return jsonify(msg='')
