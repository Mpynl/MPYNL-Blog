#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/15 18:57
# @Author  : Mpynl
# @File    : forms.py

from wtforms import Form, StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo
from flask_wtf import FlaskForm
from mysql_util import MysqlUtil

# 创建登录表单类
class LoginForm(FlaskForm):
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='请输入用户名'),
            Length(min=4, max=25, message='长度在4-25个字符之间')
        ]
    )
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20, message='长度在6-20个字符之间')
        ]
    )

    def validate_username(self, field):
        "根据用户名查找user表中记录"
        sql = "SELECT * FROM users WHERE username='%s'" % (field.data)
        db = MysqlUtil()
        result = db.fetchone(sql)
        if not result:
            raise ValidationError("用户名不存在")

class RegisterForm(FlaskForm):
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='请输入用户名'),
            Length(min=4, max=25, message='长度在4-25个字符之间')
        ]
    )
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20, message='长度在6-20个字符之间'),
            EqualTo("confirm", message="两次输入的密码不一致")
        ]
    )
    email = StringField(
        '邮箱',
        validators=[
            DataRequired(message='邮箱不能为空'),
            Email(message="邮箱格式不正确")
        ]
    )
    confirm = PasswordField(
        '确认密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20, message='长度在6-20个字符之间'),
            EqualTo("password", message="两次输入的密码不一致")
        ]
    )
    def validate_username(self, field):
        "根据用户名查找user表中记录"
        sql = "SELECT * FROM users WHERE username='%s'" % (field.data)
        db = MysqlUtil()
        result = db.fetchone(sql)
        if result:
            raise ValidationError("用户名已存在")

    def validate_email(self, field):
        "根据邮箱查找user表中记录"
        sql = "SELECT * FROM users WHERE email='%s'" % (field.data)
        db = MysqlUtil()
        result = db.fetchone(sql)
        if result:
            raise ValidationError("邮箱已经被占用！")

class ChangePasswordForm(FlaskForm):
    """
    修改密码表单
    """
    old_password = PasswordField(
        '原密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20, message='长度在6-20个字符之间'),
            EqualTo("confirm", message="两次输入的密码不一致")
        ]
    )
    new_password = PasswordField(
        '新密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20, message='长度在6-20个字符之间'),
            EqualTo("confirm", message="两次输入的密码不一致")
        ]
    )
    confirm = PasswordField(
        '确认新密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20, message='长度在6-20个字符之间'),
            EqualTo("new_password", message="两次输入的密码不一致")
        ]
    )

class ArticleForm(FlaskForm):
    title = StringField(
        '标题',
        validators=[
            DataRequired(message='长度在2-30个字符'),
            Length(min=2, max=30)
        ]
    )
    content = TextAreaField(
        '内容',
        validators=[
            DataRequired(message='长度不小于5个字符'),
            Length(min=5)
        ]
    )

class UserCenter(FlaskForm):
    # 个人中心表单
    pass