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
from flask import request, jsonify, render_template
from rrd.store import db
from rrd.model.user import User
from rrd.model.team import Team
from rrd.model.portal.template import Template
from rrd.model.portal.action import Action
from rrd.model.portal.host_group import HostGroup
from rrd.model.portal.host import Host
from rrd.model.portal.expression import Expression
from rrd.model.portal.strategy import Strategy
from rrd.model.portal.hook import Hook
from rrd.model.portal.group_host import GroupHost
from rrd.model.portal.variable import Variable
from rrd.model.portal.metric import Metric
from rrd.model.portal.tag import Tag
from rrd import corelib, config

from rrd.utils.logger import logging

log = logging.getLogger(__file__)


@app.route("/favicon.ico")
def favicon():
    return ""


@app.route('/api/version')
def api_version():
    return '2.0.0'


@app.route('/api/health')
def api_health():
    return 'ok'

@app.route('/v3/api/test', methods=['GET', 'POST', 'DELETE', 'PUT'])
def api_test():
    return jsonify(request.args)

@app.route('/api/user/<int:user_id>/inteams/<team_names>')
def api_user_in_teams(user_id, team_names):
    u = User.get_by_id(user_id)
    if not u:
        return jsonify(data=False)
    team_list = team_names.split(",") or []
    if u.in_teams(team_list):
        return jsonify(data=True)
    else:
        return jsonify(data=False)


@app.route('/api/uic/group')
def api_query_uic_group():
    q = request.args.get('query', '').strip()
    limit = int(request.args.get('limit', '10'))

    teams = Team.get_teams(q, limit)
    log.debug(teams)

    r = [x.dict() for x in teams]
    return jsonify(data=r)


@app.route('/api/template/query')
def api_template_query():
    q = request.args.get('query', '').strip()
    limit = int(request.args.get('limit', '10'))
    ts, _ = Template.query(1, limit, q)
    ts = [t.to_json() for t in ts]
    return jsonify(data=ts)


@app.route('/api/template/<tpl_id>')
def api_template_get(tpl_id):
    tpl_id = int(tpl_id)
    t = Template.get(tpl_id)
    if not t:
        return jsonify(msg='no such tpl')

    return jsonify(msg='', data=t.to_json())


@app.route('/api/action/<action_id>')
def api_action_get(action_id):
    action_id = int(action_id)
    a = Action.get(action_id)
    if not a:
        return jsonify(msg="no such action")

    return jsonify(msg='', data=a.to_json())


@app.route("/api/expression/<exp_id>")
def api_expression_get(exp_id):
    exp_id = int(exp_id)
    expression = Expression.get(exp_id)
    if not expression:
        return jsonify(msg="no such expression")
    return jsonify(msg='', data=expression.to_json())


@app.route("/api/strategy/<s_id>")
def api_strategy_get(s_id):
    s_id = int(s_id)
    s = Strategy.get(s_id)
    if not s:
        return jsonify(msg="no such strategy")
    return jsonify(msg='', data=s.to_json())


@app.route('/api/metric/query')
def api_metric_query():
    q = request.args.get('query', '').strip()
    limit = int(request.args.get('limit', '10'))

    h = {"Content-type": "application/json"}
    r = corelib.auth_requests("GET", "%s/metric/default_list" % (config.API_ADDR,), headers=h)
    if r.status_code != 200:
        log.error("%s:%s" % (r.status_code, r.text))
        return []

    metrics = r.json() or []
    metrics = [q, ] + metrics

    return jsonify(data=[{'name': name} for name in metrics])


# 给ping监控提供的接口
@app.route('/api/pings')
def api_pings_get():
    names = db.query_column("select hostname from host")
    return jsonify(hosts=names)


@app.route('/api/debug')
def api_debug():
    return render_template('portal/debug/index.html')


@app.route('/api/group/<grp_name>/hosts.json')
def api_group_hosts_json(grp_name):
    group = HostGroup.read(where='id = %s', params=[grp_name])
    if not group:
        group = HostGroup.read(where='grp_name = %s', params=[grp_name])
        if not group:
            return jsonify(msg='no such group %s' % grp_name)

    vs, _ = Host.query(1, 10000000, '', '0', group.id)
    names = [v.hostname for v in vs]
    return jsonify(msg='', data=names)


@app.route('/v3/api/host/<hostname>/variables', methods=['GET'])
def api_host_variables(hostname):
    host = Host.read(where='hostname = %s', params=[hostname])
    if not host:
        return jsonify(msg='no such host %s' % hostname)

    groups_host = GroupHost.select_vs(where='host_id = %s' % host.id)
    if not groups_host:
        return jsonify(msg='the host %s has no group attribute' % hostname)

    data = []
    for gh in groups_host:
        variables = Variable.select_vs(where='grp_id = %s' % gh.grp_id)
        for v in variables:
            data.append({'key': v.name, 'value': v.content, 'note': v.note})

    return jsonify(msg='ok', data=data)


@app.route('/v3/api/hooks', methods=['GET'])
def api_get_hook():
    hooks = Hook.select_vs()
    if not hooks:
        return jsonify(msg='Could not find any hooks')

    data = []
    for hook in hooks:
        data.append(hook.to_json())
    return jsonify(msg='ok', data=data)


@app.route('/v3/api/metrics', methods=['GET'])
def api_metrics_query():
    q = request.args.get('query', '').strip()
    if not q:
        return jsonify(data=[])
    limit = int(request.args.get('limit', '10'))
    where = "name like '%%{q}%%'".format(q=q)
    metrics = Metric.select_vs(where=where, limit=limit)
    data = [{'name': q}]
    for metric in metrics:
        data.append({'name': metric.name})
    return jsonify(data=data)

@app.route('/v3/api/tags', methods=['GET'])
def api_tags_query():
    q = request.args.get('query', '').strip()
    if not q:
        return jsonify(data=[])
    limit = int(request.args.get('limit', '10'))
    where = "name like '%%{q}%%'".format(q=q)
    tags = Tag.select_vs(where=where, limit=limit)
    data = [{'name': q}]
    for tag in tags:
        data.append({'name': tag.name})
    return jsonify(data=data)
