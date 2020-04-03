import functools
import pdb
#functools指那些作用于函数或者返回其它函数的函数，
#通常只要是可以被当做函数调用的对象就是这个模块的目标。
from flask import (Blueprint,flash,g,
                   redirect,render_template,request,session,url_for)

from werkzeug.security import check_password_hash,generate_password_hash
from flaskr.db import get_db

#定义蓝图
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register',methods=('GET','POST'))
#URL地址/register与register视图方法联系起来。
#当Flask接收到一个跳转到到/auto/register的请求时，它会调用register视图方法并使用其返回值作为响应。
def register():
    if request.method == 'POST':
    #如果用户提交表单，request.method会变成‘POST’。在这种情形下，将开始验证输入
        username = request.form['username']
        #request.form用于映射提交的表单的键和值
        #验证用户名
        password = request.form['password']
        #验证密码
        gender = request.form['gender']
        #性别
        school = request.form['school']
        #学校
        role_id = request.form['role']
        #用户组
        if role_id == "superuser":
            role_id = 1
        else:
            role_id = 2
        #用于区分是否为超级用户
        db = get_db()
        #链接数据库
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not gender:
            error = 'Gender is required.'
        elif not school:
            error = 'School is required.'
        elif db.execute('SELECT id FROM user WHERE username = ?',(username,)).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
        #以上为应对各种输入出错的返回值
        if error is None:
            db.execute('INSERT INTO user (username, password, gender, school, role_id) VALUES (?,?,?,?,?)', (username, generate_password_hash(password), gender, school, role_id))
            #创建用户表单并添加数据
            db.commit()
            #提交之前的数据，并写入数据库
            return redirect(url_for('auth.login'))
            #重定向函数调用，来到用户登录界面
        #以上为输入全部成功的返回值
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login',methods=('GET','POST'))
def login():
    #登陆函数
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        #将以上检查的用户数据保存到user里
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        #用户名或密码不匹配的时候返回的错误
        if error is None:
            session.clear()
            #清除sesstion中的数据存储
            session['user_id'] = user['id']
            #存入新的用户数据
            return redirect(url_for('index'))
            #
        #没有错误时
        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    #检查用户id是否被存储在session中，
    # 并且从数据库中获取这个用户的数据，存入g.user中长期存在
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    #如果id不存在，g.user设为空，否则将用户id存入其中
@bp.route('/logout')
def logout():
    #注销块
    session.clear()
    #移除用户数据
    return redirect(url_for('index'))


def login_required(view):
    #这个装饰器会提醒没有进行登陆就操作博客的用户进行登陆
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/users',methods=('GET','POST'))
@login_required
def get_users():
    # if request.method == 'POST':
    db = get_db()
    posts = db.execute('SELECT username,gender,school,role_id FROM user').fetchall()
    return render_template('auth/users.html', posts=posts)
