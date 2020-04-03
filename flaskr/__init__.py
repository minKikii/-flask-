#! /usr/bin/env python
# coding=utf-8
from flask import Flask
import os
from flaskr import db, auth, blog


# 在实例文件夹下加入包db，auth，blog三个文件
# 实例文件夹就是这个程序所在的文件夹
def create_app(test_config=None):  # 工程函数
    app = Flask(__name__, instance_relative_config=True)
    # 这行代码用于创建程序实例
    # __name__用于知道自己开始的路径
    # instance_relative_config=True
    # 实例文件夹位于flaskr包之外，保存一些不能上传到版本控制的本地数据，例如配置密码以及数据库文件。
    # 这个配置告诉app读取与实例文件夹相关的配置文件
    app.config.from_mapping(
        # （内置配置文件）这个设置了app会用到的默认配置
        # http://www.cnblogs.com/luna-hehe/p/9104748.html这边有app.config配置详解(不过看了看不懂还是别看了)
        SECRET_KEY='dev',
        # 密钥，Flask及其扩展用来保证数据安全的配置。
        # 这里使用简单的‘dev’，实际环境中应该使用强随机字符
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        # DATABASE 存储sqlite文件所在的位置
        # 这里是位于app.instance_path目录下，也就是实例文件夹下(instance文件夹下)
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
        # 在实例文件夹中  config.py 文件的值重写默认配置
        # 如果配置文件config.py存在，则会覆盖默认配置，例如可以用来配置一个强壮的SECRET
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
        # 保证 app.instance_path 的存在，
        # Flask不会自动穿件这个实例文件，但是他需要被创建，因为你的工程将会在这里创建 SQLite 数据库文件。
    except OSError:
        pass

    @app.route('/hello')
    # 创建一个简单的路径，创建URL/hello和返回一个response的函数之间的连接
    def hello():
        return 'Hello,fandong!'

    db.init_app(app)

    app.register_blueprint(auth.bp)

    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
