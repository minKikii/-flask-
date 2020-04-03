#! /usr/bin/env python
# coding=utf-8
import sqlite3
import click
#命令行执行数据库
from flask import current_app, g
from flask.cli import with_appcontext


def init_db():
    # 构建初始化数据库函数
    # 此函数在命令行中使用，仅一次，再次使用会删除数据库中已有数据。
    db = get_db()

    with current_app.open_resource('schemal.sql') as f:
        # open_resource()辅助函数，可以打开应用提供的资源
        db.executescript(f.read().decode('utf8'))
        # 这是一个非标准的可以在一次调用方便地执行多句SQL语句的方法。
        # 它首先发出一个COMMIT语句，之后执行SQL语句。
        # 后面筐里是 读取文本 并转换成utf-8格式
#定义了一个名为init-db的命令行命令。
#该命令行的功能主要是调用上面定义的init_db函数并给用户展示一个数据库初始化成功的信息。
#可以阅读 Command Line Interface来了解如何编写命令

@click.command('init-db')
#定义了一个名为init-db的命令行命令。
#该命令行的功能主要是调用上面定义的init_db函数并给用户展示一个数据库初始化成功的信息。
#可以阅读 Command Line Interface来了解如何编写命令
@with_appcontext
#向上下文请求注册一个函数
def init_db_command():
    init_db()
    click.echo('Initialized the database.')
    # 输出结果，使用echo进行输出是为了更好的兼容性
    # 顺带一提括号里的意思是初始化数据库


def init_app(app):
    app.teardown_appcontext(close_db) #teardown_appcontext()本质是一个装饰器，
    # 将在每次close_db(也就是底下那个断开连接函数)请求结束时调用，
    # 作用为向请求上下文中注册一个函数
    app.cli.add_command(init_db_command)
    # cli.add_command()同上本质是一个装饰器
    # 将在每次执行init_db_command时得到一个应用程序上下文
    # 作用为使你的命令和扩展有权访问app和它的配置


def get_db():
    # 辅助函数，首次调用时为当前环境船舰一个数据库连接
    # 调用成功后返回已经建立好的连接
    # 也就是说这个函数用于链接数据库
    if 'db' not in g:
        # 如果本db文件没有连接到数据库那么让他连接
        g.db = sqlite3.connect(current_app.config['DATABASE'],
                               detect_types=sqlite3.PARSE_DECLTYPES
                               )
        # sqlite3.connect创建数据库，这个函数用于建立数据库连接
        # 写了路径就是创建在硬盘上，写特定文件名memory就是创建在内存上
        g.db.row_factory = sqlite3.Row
        # 转换默认的查询数据类型为字典类型，也可以使用make_dicts
    return g.db


def close_db(e=None):
    # 断开连接数据库函数
    db = g.pop('db', None)
    if db is not None:
        db.close()