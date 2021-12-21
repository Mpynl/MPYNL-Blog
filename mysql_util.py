#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/15 18:57
# @Author  : Mpynl
# @File    : mysql_util.py

import pymysql
import traceback
import sys

class MysqlUtil():
    def __init__(self):
        """
        初始化方法，连接数据库
        """
        host = '127.0.0.1'  # 你的数据库地址
        user = 'root'       # 你的数据库用户
        password = 'xxxxxxx'  # 你的数据库连接密码
        database = 'blog'     # 博客使用的数据库
        self.db = pymysql.connect(
            host=host, user=user, password=password, db=database
        )                           # 建立连接
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)

    def insert(self, sql):
        """
        插入数据库
        :param sql: 插入数据库的SQL语句
        :return: 无
        """
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except Exception as e:
            # 如果发生异常，则回滚
            print("发生异常", e)
            self.db.rollback()
        finally:
            # 最终关闭数据库连接
            self.db.close()

    def fetchone(self, sql):
        """
        查询数据库：单个结果集
        fetchone(): 该方法获取下一个查询结果集。结果集是一个对象
        :param sql:
        :return:
        """
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
        except:
            # 输出异常信息
            traceback.print_exc()
            # 如果发生异常，则回滚
            self.db.rollback()
        finally:
            # 最终关闭数据库连接
            self.db.close()
        return result

    def fetchall(self, sql):
        """
        查询数据库：多个结果集
        fetchall()：接收全部的返回结果行
        :param sql:
        :return:
        """
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
        except:
            # 输出异常信息
            info = sys.exc_info()
            print(info[0], ":", info[1])
            # 如果发生异常，则回滚
            self.db.rollback()
        finally:
            # 最终关闭数据库连接
            self.db.close()
        return results

    def delete(self, sql):
        """
        删除结果集
        """
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            self.db.commit()
        except:
            # 将错误日志输入目录文件中
            f = open("log.txt", 'a')
            traceback.print_exc(file=f)
            f.flush()
            f.close()
            # 如果发生异常，则回滚
            self.db.rollback()
        finally:
            # 最终关闭数据库连接
            self.db.close()

    def update(self, sql):
        """
        更新结果集
        :param sql:
        :return:
        """
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            self.db.commit()
        except:
            # 如果发生异常则回滚
            self.db.rollback()
        finally:
            # 最终关闭连接
            self.db.close()