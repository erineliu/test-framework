#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2016-2021  Ben Zou <ben_zou@wistron.com>
# This file is part of Plumas project.

'''This file is part of Plumas project, it helps to access sqlite db.
'''
import os
import time
import sys

import sqlite3

DB_FILE_PATH = 'dock.db'


class SQL(object):

    def get_conn(self,path):
        '''获取到数据库的连接对象，参数为数据库文件的绝对路径，如果传递的参数是存在，并
        且是文件，那么就返回硬盘上面该路径下的数据库文件的连接对象；否则，返回内存中的数
        据链接对象
        '''
        conn = sqlite3.connect(path)
        if os.path.exists(path) and os.path.isfile(path):
            return conn
        else:
            conn = None
            return sqlite3.connect(':memory:')


    def get_cursor(self,conn):
        '''该方法是获取数据库的游标对象，参数为数据库的连接对象，如果数据库的连接对象不
        为None,则返回数据库连接对象所创建的游标对象；否则返回一个游标对象，该对象是内存
        中数据库连接对象所创建的游标对象
        '''
        if conn is not None:
            return conn.cursor()
        else:
            return get_conn('').cursor()


    def drop_table(self,conn, table):
        '''如果表存在，则删除表'''
        if table is not None and table != '':
            sql = 'DROP TABLE IF EXISTS ' + table
            cu = self.get_cursor(conn)
            cu.execute(sql)
            conn.commit()
            self.close_all(conn, cu)
        else:
            print('the [%s] is empty or equal None!', sql)


    def create_table(self,conn, sql):
        '''创建数据库表'''
        if sql is not None and sql != '':
            cu = self.get_cursor(conn)
            cu.execute(sql)
            conn.commit()
            self.close_all(conn, cu)
        else:
            print('the [%s] is empty or equal None!', sql)



    def close_all(self,conn, cu):
        '''关闭数据库游标对象和数据库连接对象'''
        if cu is not None:
            cu.close()
        if conn is not None:
            conn.close()



class MyDB(SQL):

    def dorp_tb(self):
        '''dorp table cell'''
        conn = self.get_conn(DB_FILE_PATH)
        self.drop_table(conn, 'cell')
        conn = self.get_conn(DB_FILE_PATH)
        self.drop_table(conn, "unit")


    def create_tb(self):

        '''create table cell'''

        tbl = '''CREATE TABLE cell (
                id int NOT NULL,
                item       text DEFAULT NULL,
                start_time text DEFAULT NULL,
                description text DEFAULT NULL,
                flag       int  DEFAULT 0,
                PRIMARY KEY (id)
            )'''

        tb2 = '''CREATE TABLE unit (
                id int NOT NULL,
                sn        text DEFAULT NULL,
                ip        text DEFAULT NULL,
                location  text DEFAULT NULL,
                time      text DEFAULT NULL,
                PRIMARY KEY (id)
            )'''

        conn = self.get_conn(DB_FILE_PATH)
        self.create_table(conn, tbl)

        conn = self.get_conn(DB_FILE_PATH)
        self.create_table(conn, tb2)


    def initial_data(self):

        '''initial data...'''
        sql = "INSERT INTO cell VALUES(?,'','','',0)"
        data = [(x,) for x in range(0, 81)]

        sq2 = "INSERT INTO unit VALUES(?,'','','','')"
        data2 = [(x,) for x in range(0, 21)]

        conn = self.get_conn(DB_FILE_PATH)
        cu = self.get_cursor(conn)

        cu.executemany(sql, data)
        cu.executemany(sq2, data2)

        conn.commit()
        cu.close()
        conn.close()


    def fetchall(self,table="cell"):
        '''查询所有数据'''
        sql = "SELECT * FROM %s"%(table)
        conn = self.get_conn(DB_FILE_PATH)
        cu = self.get_cursor(conn)
        cu.execute(sql)
        values = cu.fetchall()
        cu.close()
        conn.close()
        return values


    def fetch(self,min=0, max=80):
        '''查询所有数据'''
        sql = "SELECT * FROM cell limit %s, %s" % (min, max)
        conn = self.get_conn(DB_FILE_PATH)
        cu = self.get_cursor(conn)
        cu.execute(sql)
        values = cu.fetchall()
        cu.close()
        conn.close()
        return values


    def update(self,pid, pitem, pdescription, pflag):
        pstart_time = time.strftime("%X")
        sql = "update cell set item=?, start_time=?, description=?, \
            flag=? where id=?"
        conn = self.get_conn(DB_FILE_PATH)
        cu = self.get_cursor(conn)
        data = (pitem, pstart_time, pdescription, pflag, pid)
        cu.execute(sql, data)
        conn.commit()
        self.close_all(conn, cu)


    def update_state(self,pid, pdescription, pflag):
        pstart_time = time.strftime("%X")
        sql = "update cell set start_time=?, description=?, \
            flag=? where id=?"
        conn = self.get_conn(DB_FILE_PATH)
        cu = self.get_cursor(conn)
        data = (pstart_time, pdescription, pflag, pid)
        cu.execute(sql, data)
        conn.commit()
        self.close_all(conn, cu)


    def unit_update(self,pid,sn,ip,location):
        update_time = time.strftime("%X")
        sql = "update unit set sn=?, ip=?, \
            location=?,time=? where id=?"
        conn = self.get_conn(DB_FILE_PATH)
        cu = self.get_cursor(conn)
        data = (sn,ip,location,update_time, pid)
        cu.execute(sql, data)
        conn.commit()
        self.close_all(conn, cu)



    def update_data(self):
        sql = "update cell set item='', start_time='', description='', \
            flag=0 where id=?"
        data = [(x,) for x in range(0, 81)]
        conn = self.get_conn(DB_FILE_PATH)
        cu = self.get_cursor(conn)
        cu.executemany(sql, data)
        conn.commit()
        cu.close()
        conn.close()


    def create_db(self):
        self.dorp_tb()
        self.create_tb()
        self.initial_data()



    def result2flag(self,result):
        mapDict={"PASS":2,"FAIL":3}
        return mapDict[result]



    def flag2result(self,pid):
        if pid == 1:
            return "Testing"
        elif pid == 2:
            return "PASS"
        elif pid > 2:
            return "FAIL"
        else:
            return ""

'''
def main():
    if len(sys.argv) == 3:
        values = fetch(sys.argv[1], sys.argv[2])
    else:
        values = fetchall()
    for v in values:
        print(v)
'''

mydb = MyDB()


if __name__ == '__main__':

    ## pid ##
    # unstart:0  testing: 1  pass: 2  fail: 3  Unknow: 4  start failed: 5
    # 1 -> #FFFF00 - yellow
    # 2 -> #00FF00 - green
    # 3 -> #FF0000 - red
    # 4 -> #FF0000 - red

    #create_db()
    #main()

    db1 = MyDB()
    db1.create_db()
    db1.unit_update(1,"abb","123","s")


    '''
    cell_id = 0

    db1.update(cell_id, '', '', 0)
    db1.update(cell_id + 1, 'usb test', '', 0)
    db1.update(cell_id + 2, '', '', 0)
    db1.update(cell_id + 3, '', '', 0)

    db1.update_state(cell_id + 1, "hello", 4)
    '''




