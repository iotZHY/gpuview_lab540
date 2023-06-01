#!/usr/bin/env python

"""
Web API of gpuview.

@author Fitsum Gaim
@url https://github.com/fgaim
"""

import os
import json
from datetime import datetime

from flask import redirect, url_for, render_template, request, Flask, jsonify
from flask_login import LoginManager, login_required, logout_user, login_user, current_user

import utils
import core
from login import *

abs_path = os.path.dirname(os.path.realpath(__file__))
abs_views_path = os.path.join(abs_path, 'views')
app = Flask(__name__, template_folder=abs_views_path)


app.secret_key = 'abc'
login_manager = LoginManager()  # 实例化登录管理对象
login_manager.init_app(app)  # 初始化应用
login_manager.login_view = 'login'  # 设置用户登录视图函数 endpoint


@app.route('/login/', methods=('GET', 'POST'))  # 登录
def login():
    if request.method == 'POST':
        user_name = request.form.get('username')
        password = request.form.get('password')
        user_info = get_user(user_name)  # 从用户数据中查找用户记录
        if user_info is None:
            emsg = "用户名或密码密码有误"
        else:
            user = User(user_info)  # 创建用户实体
            if user.verify_password(password):  # 校验密码
                login_user(user)  # 创建用户 Session
                return redirect(request.args.get('next') or url_for('index'))
            else:
                emsg = "用户名或密码密码有误"
    return render_template('login.html')


@login_manager.user_loader  # 定义获取登录用户的方法
def load_user(user_id):
    return User.get(user_id)

@app.route('/logout')  # 登出
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    gpustats = core.all_gpustats()
    now = datetime.now().strftime('Updated at %Y-%m-%d %H-%M-%S')
    return render_template('index.html', gpustats=gpustats, update_time=now, username = current_user.username)


@app.route('/gpustat', methods=['GET'])
def report_gpustat():
    """
    Returns the gpustat of this host.
        See `exclude-self` option of `gpuview run`.
    """

    def _date_handler(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError(type(obj))
    resp = core.my_gpustat()
    return jsonify(resp)


def main():
    parser = utils.arg_parser()
    args = parser.parse_args()

    if 'run' == args.action:
        core.safe_zone(args.safe_zone)
        core.exclude_self(args.exclude_self)
        app.run(host=args.host, port=args.port, debug=args.debug)
    elif 'service' == args.action:
        core.install_service(host=args.host,
                             port=args.port,
                             safe_zone=args.safe_zone,
                             exclude_self=args.exclude_self)
    elif 'add' == args.action:
        core.add_host(args.url, args.name)
    elif 'remove' == args.action:
        core.remove_host(args.url)
    elif 'hosts' == args.action:
        core.print_hosts()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
