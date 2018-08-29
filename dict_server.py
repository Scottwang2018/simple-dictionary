#!/usr/bin/env python3
#coding=utf-8

'''
name:Scott
data:2018-08-27
E-mail:scott2018.163.com
modules:python3.5 mysql pymysql
This is a dict project for AID
'''

from socket import *
import os
import pymysql
import time
import sys
import signal

DICT_TEXT = "./dict.txt"
HOST = '0.0.0.0'
PORT = 8000
ADDR = (HOST,PORT)

# 主控制流程
def main():
    # 连接数据库
    db = pymysql.connect\
    ('localhost','root','123456','dict')

    # 创建流式套接字
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)
    # 忽略子进程退出
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    while True:
        try:
            c,addr = s.accept()
            print("Connect from:",addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务器退出")
        except Exception as e:
            print("Error:",e)
            continue
        # 创建子进程处理客户端请求
        pid =os.fork()
        if pid == 0:
            s.close()
            do_child(c,db)
        else:
            c.close()

def do_child(c,db): 
    # 循环接收请求
    while True:
        data = c.recv(128).decode()
        print("Receive:",data)

        if (not data) or data[0] == "E":  #客户端ctrl-c退出或退出
            c.close()
            sys.exit(0)
        elif data[0] == "R":
            do_register(c,db,data)
        elif data[0] == "L":
            do_login(c,db,data)
        elif data[0] == "Q":
            do_query(c,db,data)
        elif data[0] == "H":
            do_history(c,db,data)

def do_register(c,db,data):
    l = data.split(" ")
    name = l[1]
    passwd = l[2]

    cursor = db.cursor()
    sql = \
    "select * from user where name='%s'"%name
    cursor.execute(sql)
    r = cursor.fetchone()
    if r != None:
        c.send(b"EXISTS")
        return

    sql = "insert into user (name,passwd)\
        values('%s','%s')"%(name,passwd)
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b"OK")
    except:
        db.rollback()
        c.send(b"Fail")
    else:
        print("%s注册成功"%name)

def do_login(c,db,data):
    l = data.split(" ")
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()

    sql = "select * from user where \
    name='%s' and passwd='%s'"%(name,passwd)

    cursor.execute(sql)
    r = cursor.fetchone()
    if r == None:
        c.send("用户名或密码不正确".encode())
    else:
        c.send(b"OK")

def do_query(c,db,data):
    l = data.split(" ")
    name =l[1]
    word = l[2]
    cursor = db.cursor()

    def insert_history():   #定义内部函数
        tm = time.ctime()
        sql = "insert into hist (name,word,time)\
         values ('%s','%s','%s')"%(name,word,tm)

        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print("Error:",e)
            db.rollback()
            return

    try:
        f = open(DICT_TEXT,'rb')
    except:
        c.send("500 服务端异常".encode())
        return
    while True:
        line = f.readline().decode()
        w = line.split(" ")[0]
        if (not line) or w > word:
            c.send("没有找到该单词".encode())
            break
        elif w == word:
            c.send(b"OK")
            time.sleep(0.1)
            c.send(line.encode())
            insert_history()
            break
    f.close()

def do_history(c,db,data):
    name = data.split(" ")[1]
    cursor = db.cursor()

    try:
        sql = "select * from hist where name='%s'"%name
        cursor.execute(sql)
        r = cursor.fetchall()
        if not r:
            c.send("没有历史记录".encode())
            return
        else:
            c.send(b"OK")
    except Exception as e:
        print("Error:",e)
        c.send("数据库查询错误".encode())
        return
    n = 0
    for i in r:
        n += 1
        # 最多显示10条
        if n > 10:
            break
        time.sleep(0.03)
        msg = "%s   %s   %s"%(i[1],i[2],i[3])

        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b"##")

if __name__=='__main__':
    main()