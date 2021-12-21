#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/15 18:57
# @Author  : Mpynl
# @File    : manage.py

from flask import Flask, render_template, session, redirect, url_for, request, flash
from passlib.hash import sha256_crypt
from mysql_util import MysqlUtil
from forms import LoginForm, RegisterForm, ChangePasswordForm, ArticleForm
from functools import wraps
import time

app = Flask(__name__)
app.secret_key = '*ZJG4_@v5QViwaFqzB86.,r%Zp2wRma!'

@app.route('/')
def index():
    db = MysqlUtil()
    count = 3    # 每页显示数量
    page = request.args.get('page')
    if page is None:
        page = 1
    sql = f'SELECT * FROM articles ORDER BY create_date DESC LIMIT {(int(page)-1)*count}, {count}'
    articles = db.fetchall(sql)
    return render_template('home.html', articles=articles, page=int(page))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # 用户注册
    if "logged_in" in session:
        return redirect(url_for("dashboard"))
    form = RegisterForm(request.form)
    if form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(form.password.data)
        email = form.email.data
        create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db = MysqlUtil()
        sql = "INSERT INTO users (username, password, email, create_time) " \
              "VALUES ('%s', '%s', '%s', '%s')" % (username, password, email, create_time)
        db.insert(sql)
        flash("用户创建成功", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 用户登录
    if "logged_in" in session:
        return redirect(url_for("dashboard"))

    form = LoginForm(request.form)
    if form.validate_on_submit():
        # 从表单中获取字段
        username = request.form['username']
        password_candidate = request.form['password']
        # 根据用户名查找user表中记录
        sql = "SELECT * FROM users WHERE username='%s'" % (username)
        db = MysqlUtil()
        result = db.fetchone(sql)
        password = result['password']
        # 对比用户填写的密码和数据库中记录的密码是否一致
        # 调用verify方法验证，如果为真，验证通过
        if sha256_crypt.verify(password_candidate, password):
            # 写入session
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('用户名和密码不匹配', 'danger')

    return render_template('login.html', form=form)

# 如果用户已经登录
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:     # 判断用户是否登录
            return f(*args, **kwargs)  # 如果登录，继续执行被装饰的函数
        else:                          # 如果没有登录，提示无权访问
            flash('无权访问，请先登录', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/change_password', methods=['GET', 'POST'])
@is_logged_in
def change_password():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        db = MysqlUtil()
        sql = "SELECT password FROM users WHERE username='%s'" % (session['username'])
        result = db.fetchone(sql)
        old_password = result['password']
        old_password_input = form.old_password.data
        new_password_input = form.new_password.data
        new_password = sha256_crypt.encrypt(form.new_password.data)
        if sha256_crypt.verify(old_password_input, old_password):
            if not sha256_crypt.verify(new_password_input, old_password):
                try:
                    db = MysqlUtil()
                    sql = "UPDATE users SET password='%s', last_password='%s' WHERE username='%s'" \
                          % (new_password, old_password, session['username'])
                    db.update(sql)
                    flash("密码修改成功", "success")
                except Exception as e:
                    flash("密码修改失败")
            else:
                flash("两次密码不能一样，请重新输入", 'danger')
        else:
            flash("原密码输入有误，请重新输入", "danger")
    return render_template('/change_password.html', form=form)



@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("您已成功退出", 'success')
    return redirect(url_for('index'))

@app.route('/change_user')
@is_logged_in
def change_user():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    db = MysqlUtil()
    sql = "SELECT * FROM articles WHERE author='%s' ORDER BY create_date DESC" % (session['username'])
    result = db.fetchall(sql)
    if result:
        return render_template('dashboard.html', articles=result)
    else:
        msg = '暂无博客信息'
        return render_template('dashboard.html', msg=msg)

@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        content = form.content.data
        author = session['username']
        create_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db = MysqlUtil()
        sql = "INSERT INTO articles(title, content, author, create_date)" \
              "VALUES ('%s', '%s', '%s', '%s')" %(title, content, author, create_date)
        db.insert(sql)
        flash('创建成功', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)

@app.route('/article/<string:id>')
def article(id):
    db = MysqlUtil()
    sql = "SELECT * FROM articles WHERE id='%s'" %(id)
    article = db.fetchone(sql)
    return render_template('article.html', article=article)

@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    db = MysqlUtil()
    fetch_sql = "SELECT * FROM articles WHERE id='%s' and author='%s'" % (id, session['username'])
    article = db.fetchone(fetch_sql)
    # 检测博客不存在的情况
    if not article:
        flash("ID错误", 'danger')
        return redirect(url_for('dashboard'))
    # 获取表单
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        # 获取表单字段内容
        title = form.title.data
        content = form.content.data
        update_sql = "UPDATE articles SET title='%s', content='%s' WHERE id='%s' and author='%s'" % (
            title, content, id, session['username'])
        db = MysqlUtil()
        db.update(update_sql)
        flash("修改成功", 'success')
        return redirect(url_for('dashboard'))

    # 从数据库中获取表单字段的值
    form.title.data = article['title']
    form.content.data = article['content']
    return render_template('edit_article.html', form=form)

@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    db = MysqlUtil()
    sql = "DELETE FROM articles WHERE id='%s' and author='%s'" % (id, session['username'])
    db.delete(sql)
    flash("删除成功", 'success')
    return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(error):
    """
    404
    :param error:
    :return:
    """
    return render_template("/404.html"), 404

if __name__ == '__main__':
    app.run(debug=True,
            host='0.0.0.0',
            port=8080)