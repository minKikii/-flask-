from flask import (Blueprint, flash, g,redirect,render_template,request,url_for)
#Blueprint蓝图，是flax的子集，它可以有独立的templates、static等。
#而模块独立可以使整个工程变得清晰易读，也避免文件之间循环引用的问题
#flash 带给用户良好的体验和反馈
#redirect重定向  浏览器返回用户提交的数据时，需要重定向一个网页来处理用户表单内容
#render_temlpates,在templates文件夹中找到对应的html，不仅可以渲染静态的html文件，也能传递参数给html
#https://segmentfault.com/a/1190000012817254关于render_temlpates
#request处理请求机制，代码中用到了大量的request单独解释
#url_for用于给制定的函数构造URL
from werkzeug.exceptions import abort
#werkzrug是一个WSGI工具包，用作制作Web框架的底层库
#exceptions是其中响应错误的一块，，，由于那边全是英文太麻烦了所以就这吧
#abort函数 异常终止进程除非SIGABRT信号被捕捉并且信号处理句柄没有返回
from flaskr.auth import login_required
#实例文件夹下auth.py文件中的函数
from flaskr.db import get_db
#同上

bp = Blueprint('blog', __name__)
#创建一个蓝图，第一参数指定蓝图名称，第二个参数指定静态文件的相对路径
@bp.route('/')#添加路由装饰器
@login_required#登陆请求装饰器
def index():
    db = get_db()#链接数据库
    posts = db.execute('SELECT p.id,title,body,created,author_id, username FROM post p JOIN user u ON p.author_id = u.id ORDER BY created DESC ').fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    #创建一个新主题
    if request.method == 'POST':
        title = request.form['title']
        #题目
        body = request.form['body']
        #内容
        error = None

        if not title:
            error = 'Title is required.'
        #缺少题目
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO post (title,body,author_id) VALUES (?,?,?)',(title,body,g.user['id']))
            db.commit()
            return redirect(url_for('blog.index'))
        #各种异常状态处理，没有错误时 连接数据库 保存 写入数据库三步操作完成这次主题的编写
    return render_template('blog/create.html')

def get_post(id,check_auth=True):
    #检查博客是否存在
    post = get_db().execute('SELECT p.id,title,body,created,author_id,username FROM post p JOIN user u ON p.author_id = u.id WHERE p.id = ?', (id,)).fetchone()
    #链接数据库并将保存入数据库中的博客信息存入post变量
    if post is None:
        abort(404,"Post id {0} doesn't exist.".format(id))
    #空博客
    if check_auth and post['author_id'] != g.user['id']:
        abort(403)
    #用户名不一致
    return post

@bp.route('/<int:id>/update',methods=('GET','POST'))
@login_required
def update(id):
    #重新编辑博客，跟上面的create内容一样
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('UPDATE post SET title = ?,body = ? where id =?',(title,body,id))
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    #删除博客
    get_post(id)
    #检查博客是否存在
    db = get_db()
    #连接数据库
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    #调用存储过程为删除
    db.commit()
    #保存操作
    return redirect(url_for('blog.index'))
