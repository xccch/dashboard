#-*- coding:utf-8 -*-
# Copyright 2017 Xiaomi, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import datetime
import time
from flask import g, session, request, redirect, jsonify

from rrd import app, config
from rrd.view.utils import get_usertoken_from_session, get_current_user_profile

@app.template_filter('fmt_time')
def fmt_time_filter(value, pattern="%Y-%m-%d %H:%M"):
    if not value:
        return ''
    return datetime.datetime.fromtimestamp(value).strftime(pattern)

@app.template_filter('time_duration')
def time_duration(v):
    d = time.time() - time.mktime(v.timetuple())

    if d <= 60:
        return "just now"
    if d <= 120:
            return "1 minute ago"
    if d <= 3600:
        return "%d minutes ago" % (d/60)
    if d <= 7200:
        return "1 hour ago"
    if d <= 3600*24:
        return "%d hours ago" % (d/3600)
    if d <= 3600*24*2:
        return "1 day ago"

    return "%d days ago" % (d/3600/24)

@app.teardown_request
def app_teardown(exception):
    from rrd.store import db, alarm_db
    db.commit()
    alarm_db.commit()

@app.before_request
def app_before():
    g.user_token = get_usertoken_from_session(session)
    g.user = get_current_user_profile(g.user_token)
    g.locale = request.accept_languages.best_match(config.LANGUAGES.keys())

    path = request.path
    if not g.user and not path.startswith("/auth/login") and \
            not path.startswith("/static/") and \
            not path.startswith("/portal/links/") and \
            not path.startswith("/auth/register") and \
            not path.startswith("/v3/"):
        return redirect("/auth/login")

    if g.user and path == "/auth/login":
        return redirect("/")

    if g.user and g.user.role == 0 and \
            path not in ['/auth/logout', '/user/profile', '/portal/hostgroup', '/screen/',  '/', '/user/chpwd'] and \
            not path.startswith('/chart') and \
            not (path.startswith('/portal/group/') and (path.endswith('/graph') or path.endswith('hosts'))) and \
            not (path == '/api/counters' and request.method == 'POST') and \
            not (path == '/api/endpoints' and request.method == 'GET'):
        return jsonify({'msg': 'You have no permission'})

    if path.startswith("/screen"):
        g.nav_menu = "nav_screen"
    elif path.startswith("/portal/hostgroup") or path.startswith("/portal/group"):
        g.nav_menu = "p_hostgroup"
    elif path.startswith("/portal/template"):
        g.nav_menu = "p_template"
    elif path.startswith("/portal/expression"):
        g.nav_menu = "p_expression"
    elif path.startswith("/portal/nodata"):
        g.nav_menu = "p_nodata"
    elif path.startswith("/portal/alarm-dash"):
        g.nav_menu = "p_alarm-dash"
    elif path.startswith("/portal/metric") or path.startswith("/portal/tag"):
        g.nav_menu = "p_metric"
    else:
        g.nav_menu = ""
