# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str
from .OUCJW import OucJw
import urllib.request
import urllib.parse
import http.cookiejar
import pymysql
import json
import chardet
import hashlib
import sys
import time
from lxml import etree
TOKEN = "zqx123321a"


def printf(content):
    db = pymysql.connect("localhost","root","","login")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()      
    # 使用 execute() 方法执行 SQL，如果表存在则删除
    sql="insert into logg values('"+content+"')"
    cursor.execute(sql)
    # 提交到数据库执行
    try:
        db.commit()     
    except:
        db.rollback()
def insertUser(ID,username,password):
    try:
        global oucjw
        res = json.loads(oucjw.login(username, password))
        status=res["status"]
        if status=="200":
            db = pymysql.connect("localhost","root","","login")
            # 使用 cursor() 方法创建一个游标对象 cursor
            cursor = db.cursor()      
            # 使用 execute() 方法执行 SQL，如果表存在则删除
            sql="insert into wechat_user(openid,username,password) values('"+ID+"','"+username+"','"+password+"')"
            cursor.execute(sql)
           # 提交到数据库执行
            try:
                db.commit()
                return "绑定成功!"
            except:
               # # 如果发生错误则回滚
                db.rollback()
                return "绑定失败！"
        else:
            return "用户名密码不正确！"
    except:
         return "绑定失败！"

def checkIshere(ID):
    try:
        conn=pymysql.connect("localhost","root","","login")
        cur=conn.cursor()
        cur.execute('select * from wechat_user where openid=%s',ID)
        result=cur.fetchone()
        cur.close()
        conn.close()
        if result==None:                                                          
            return -1
        else:
            username=result[1]
            password=result[2]
            global oucjw
            res = json.loads(oucjw.login(username, password))
            status=res["status"]
            if status=="200":
                return 1
            else:
                return 0
    except:
        return -1

@csrf_exempt
def handleRequest(request):
    if request.method == 'GET':
        #下面这四个参数是在接入时，微信的服务器发送过来的参数
        signature = request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echostr = request.GET.get('echostr', None)

        #这里的token需要自己设定，主要是和微信的服务器完成验证使用
        token = 'zqx123321a'

        #把token，timestamp, nonce放在一个序列中，并且按字符排序
        hashlist = [token, timestamp, nonce]
        hashlist.sort()

        #将上面的序列合成一个字符串
        hashstr = ''.join([s for s in hashlist])

        #通过python标准库中的sha1加密算法，处理上面的字符串，形成新的字符串。
        hashstr = hashlib.sha1(hashstr.encode(encoding='utf-8')).hexdigest()

        #把我们生成的字符串和微信服务器发送过来的字符串比较，
        #如果相同，就把服务器发过来的echostr字符串返回去
        if hashstr == signature:
          return HttpResponse(echostr)

    elif request.method == 'POST':
        response = HttpResponse(responseMsg(request),content_type="application/xml")
        return response
    else:
        return None



def responseMsg(request):
     #将程序中字符输出到非 Unicode 环境（比如 HTTP 协议数据）时可以使用 smart_str 方法
    data = smart_str(request.body)
    xml = etree.fromstring(data)
    fromUser = xml.find('ToUserName').text
    toUser = xml.find('FromUserName').text
    msgType = xml.find('MsgType').text
    nowtime = str(int(time.time()))
    queryStr = xml.find('Content').text
    OPENID=toUser
    msg={
        "ToUserName":fromUser,
        "FromUserName":toUser,
        "MsgType":msgType,
    }

    isHere=checkIshere(OPENID)
    content=''
    if queryStr[0:2]=="BD":
        content=insertUser(msg.get('FromUserName'),queryStr[3:14],queryStr[15:len(queryStr)])
        return getReplyXml(msg,content)
    elif isHere==-1:
        content="您还没有绑定用户名和密码，回复BD+学号+密码进行绑定，如BD 15020031000 1234567"
        return getReplyXml(msg,content)
    elif isHere==0:
        content="登录失败，请重试"
        return getReplyXml(msg,content)

    elif queryStr[0:3]=="all":
        try:
            global oucjw
            res =json.loads(oucjw.getGrade('2017', '1', 'sjxz1', queryStr[3:14]))
            content+=("姓名："+res["name"]+"\n")
            for i in res["data"]:
                content+=(i["classname"]+"："+(str(i["grade"])+"\n"))
            content+=("选课总学分："+str(res["score"])+"\n")
            content+=("加权平均分："+str(res["average"]))
        except:
            content="ERROR"
        return getReplyXml(msg,content)

    elif queryStr[0:2]=="cj":
        try:
            global oucjw
            res = json.loads(oucjw.getGrade('2017', '1', 'sjxz3', queryStr[2:13]))
            content+=("姓名："+res["name"]+"\n")
            for i in res["data"]:
                content+=(i["classname"]+"："+(str(i["grade"])+"\n"))
            content+=("选课总学分："+str(res["score"])+"\n")
            content+=("加权平均分："+str(res["average"]))
        except:
            content="ERROR"
        return getReplyXml(msg,content)

    elif queryStr[0:2]=="xh":
        try:
            db = pymysql.connect("localhost","root","","login",charset='utf8' )
            cursor = db.cursor() 
            # cursor2 = db.cursor()
            name = queryStr[2:len(queryStr)]
            like=name+'%'
            sql="select * from wechat_data where username like '"+like+"'"   
            cursor.execute(sql)
            results = cursor.fetchall()    #获取查询的所有记录 
            if(len(results)==0):
                content='查无此人'
            for row in results:  
                content+=(str(row[1])[0:11]+" "+row[5])
            db.close()
        except:
            content="ERROR"
        return getReplyXml(msg,content)
    
    else:
        return replyNew(msg)


def paraseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            msg[child.tag] = smart_str(child.text)
    return msg


def getReplyXml(msg,replyContent):
    for i in range(1,1000):
        extTpl = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>";
        extTpl = extTpl % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',replyContent)
        return extTpl



# def replytest(msg):
#     extTpl = '''<xml>
#            <ToUserName><![CDATA[%s]]></ToUserName>
#            <FromUserName><![CDATA[%s]]></FromUserName>
#            <CreateTime>%s</CreateTime>
#            <MsgType><![CDATA[%s]]></MsgType>
#            <ArticleCount>%s</ArticleCount>
#             <Articles>
#                <item>
#                    <Title><![CDATA[%s]]></Title> 
#                    <Description><![CDATA[%s]]></Description>
#                    <PicUrl><![CDATA[%s]]></PicUrl>
#                    <Url><![CDATA[%s]]></Url>
#                </item>
#         </Articles>
#         </xml>''';
#     extTpl = extTpl % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'news','1','A New World','A New World,Are You Ready?','http://www.ouctechnology.cn:8088/android/zqx/image/passage/bg.jpg','http://www.ouctechnology.cn/wechat/index/?openid='+msg['FromUserName'])
#     return extTpl

def replyNew(msg):
    extTpl = '''<xml>
           <ToUserName><![CDATA[%s]]></ToUserName>
           <FromUserName><![CDATA[%s]]></FromUserName>
           <CreateTime>%s</CreateTime>
           <MsgType><![CDATA[%s]]></MsgType>
           <ArticleCount>%s</ArticleCount>
            <Articles>
               <item>
                   <Title><![CDATA[%s]]></Title> 
                   <Description><![CDATA[%s]]></Description>
                   <PicUrl><![CDATA[%s]]></PicUrl>
                   <Url><![CDATA[%s]]></Url>
               </item>
        </Articles>
        </xml>''';
    extTpl = extTpl % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'news','1','OUC-Technology使用说明文档','OUC-Technology使用说明文档','http://www.ouctechnology.cn:8088/wechat.png','http://mp.weixin.qq.com/s/eBJpLAuwge2EXPeI0AtmRA')
    return extTpl




oucjw = OucJw()
@csrf_exempt
def login(request):
    if request.method == 'POST':
        return HttpResponse(request.POST)
    else:
        code=request.GET["code"]
        url="https://api.weixin.qq.com/sns/jscode2session"
        data={
            "appid":"wxf143edc544c82f7e",
            "secret":"323006b21f6fa4f848813b97bda73980",
            "js_code":code,
            "grant_type":"authorization_code"
        }
        url += '?' + urllib.parse.urlencode(data)  
        request = urllib.request.Request(url)  
        response = urllib.request.urlopen(request)
        html= response.read()
        #转码
        char = chardet.detect(html)
        data = html.decode(char['encoding'],'ignore')
        res = json.loads(data)
        openid=res["openid"]
   
        db = pymysql.connect("localhost","root","","login" )
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()      
        # 使用 execute() 方法执行 SQL，如果表存在则删除
        cursor.execute("select * from wechat_user where openid='"+openid+"'")      
        data = cursor.fetchone()
        db.close()
        result={}
        if data==None:                                                          
            result["success"]=0
            result["openid"]=openid
        else:
            username=data[1]
            password=data[2]
            res = json.loads(oucjw.login(username, password))
            status=res["status"]
            if status=="200":
                result["success"]=1
                result["openid"]=openid
                result["username"]=username
                result["password"]=password
            else:
                result["success"]=0
                result["openid"]=openid
        return HttpResponse(json.dumps(result))

@csrf_exempt
def bind(request):
    if request.method == 'POST':
        return HttpResponse(Request.POST)
    else:
        openid=request.GET['openid']
        username = request.GET['username']
        password = request.GET['password']
        values=[openid,username,password]
        res = json.loads(oucjw.login(username, password))
        status=res["status"]
        result={}
        if status=="200":
            db = pymysql.connect("localhost","root","","login")
            # 使用 cursor() 方法创建一个游标对象 cursor
            cursor = db.cursor()      
            # 使用 execute() 方法执行 SQL，如果表存在则删除
            sql="insert into wechat_user(openid,username,password) values('"+openid+"','"+username+"','"+password+"')"
            cursor.execute(sql)
           # 提交到数据库执行
            try:
                db.commit()
                result["success"]=1
                result["openid"]=openid
                result["username"]=username
                result["password"]=password
            except:
               # # 如果发生错误则回滚
                db.rollback()
                result["success"]=0
                result["openid"]=openid
        else:
            result["success"]=0
            result["openid"]=openid

        return HttpResponse(json.dumps(result))

@csrf_exempt
def unbind(request):
    if request.method == 'POST':
        return HttpResponse(Request.POST)
    else:
        openid=request.GET['openid']
        sql="delete from wechat_user where openid='"+openid+"'";
        db = pymysql.connect("localhost","root","","login")
        cursor = db.cursor()      
        cursor.execute(sql)
        result={}
        try:
            db.commit()
            result["success"]=1
        except:
            db.rollback()
            result["success"]=0
        return HttpResponse(json.dumps(result))
@csrf_exempt
def getGrade(request):

    if request.method == 'POST':
        xn = request.POST['xn']
        xq = request.POST['xq']
        userCode = request.POST['userCode']
        sjxz = "sjxz3"
        if xq == "3":
            sjxz = "sjxz1"
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.getGrade(xn, xq, sjxz, userCode)
        return HttpResponse(res)
    else:
        xn = request.GET['xn']
        xq = request.GET['xq']
        userCode = request.GET['userCode']
        sjxz = "sjxz3"
        if xq == "3":
            sjxz = "sjxz1"
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.getGrade(xn, xq, sjxz, userCode)
        return HttpResponse(res)

@csrf_exempt
def getUserCode(request):
    if request.method == 'POST':
        xn = request.POST['xn']
        xq = request.POST['xq']
        classCode = request.POST['classCode']
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.getUserCode(xn, xq, classCode)
        return HttpResponse(res)
    else:
        xn = request.GET['xn']
        xq = request.GET['xq']
        classCode = request.GET['classCode']
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.getUserCode(xn, xq, classCode)
        return HttpResponse(res)

@csrf_exempt
def getUserCoin(request):
    if request.method == 'POST':
        xn = request.POST['xn']
        xq = request.POST['xq']
        classCode = request.POST['classCode']
        userCode = request.POST['userCode']
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.getClassCoin(xn, xq, classCode,userCode)
        return HttpResponse(res)
    else:
        xn = request.GET['xn']
        xq = request.GET['xq']
        classCode = request.GET['classCode']
        userCode = request.GET['userCode']
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.getClassCoin(xn, xq, classCode,userCode)
        return HttpResponse(res)

@csrf_exempt
def getClassName(request):
    if request.method == 'POST':
        xn = request.POST['xn']
        xq = request.POST['xq']
        classCode = request.POST['classCode']
        userCode = request.POST['userCode']
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.getClassName(xn, xq,userCode, classCode)
        return HttpResponse(res)
    else:
        xn = request.GET['xn']
        xq = request.GET['xq']
        classCode = request.GET['classCode']
        userCode = request.GET['userCode']
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.getClassName(xn, xq,userCode, classCode)
        return HttpResponse(res)

@csrf_exempt
def getMajor(request):
    if request.method == 'POST':
        return HttpResponse(Request.POST)
    else:
        db = pymysql.connect("localhost","root","","login",charset='utf8' )
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()      
        # 使用 execute() 方法执行 SQL，如果表存在则删除
        cursor.execute("select * from wechat_majordb")      
        results = cursor.fetchall()    #获取查询的所有记录
        result={}
        lis=[]  
        for row in results:  
            dic={}
            dic["id"]=row[0]  
            dic["major"]=row[1]
            lis.append(dic)
        db.close()
        result["data"]=lis
        return HttpResponse(json.dumps(result))

@csrf_exempt
def getUser(request):
    if request.method == 'POST':
        db = pymysql.connect("localhost","root","","login",charset='utf8' )
        cursor = db.cursor() 
        # cursor2 = db.cursor()
        major = request.POST['major']
        nj = request.POST['nj']
        like=nj+'%'
        sql="select * from wechat_data,wechat_majordb where wechat_data.major=wechat_majordb.major and wechat_majordb.id="+major+" and usercode like '"+like+"'"   
        cursor.execute(sql)
        results = cursor.fetchall()    #获取查询的所有记录
        result={}
        lis=[]  
        for row in results:  
            dic={}
            dic["usercode"]=row[1][0:11]
            dic["username"]=row[2]
            dic["usersex"]=row[3]
            lis.append(dic)
        db.close()
        result["data"]=lis
        return HttpResponse(json.dumps(result))
    else:
        db = pymysql.connect("localhost","root","","login",charset='utf8' )
        cursor = db.cursor() 
        # cursor2 = db.cursor()
        major = request.GET['major']
        nj = request.GET['nj']
        like=nj+'%'
        sql="select * from wechat_data,wechat_majordb where wechat_data.major=wechat_majordb.major and wechat_majordb.id="+major+" and usercode like '"+like+"'"   
        cursor.execute(sql)
        results = cursor.fetchall()    #获取查询的所有记录
        result={}
        lis=[]  
        for row in results:  
            dic={}
            dic["usercode"]=row[1][0:11]
            dic["username"]=row[2]
            dic["usersex"]=row[3]
            lis.append(dic)
        db.close()
        result["data"]=lis
        return HttpResponse(json.dumps(result))

@csrf_exempt
def getClassTable(request):
    if request.method == 'POST':
        xn = request.POST['xn']
        xq = request.POST['xq']
        userCode = request.POST['userCode']
        global oucjw
        res =oucjw.getClassTable2(xn, xq,userCode)
        return HttpResponse(res)
    else:
        xn = request.GET['xn']
        xq = request.GET['xq']
        userCode = request.GET['userCode']
        global oucjw
        res = oucjw.getClassTable2(xn, xq,userCode)
        return HttpResponse(res)

@csrf_exempt
def getClassGrade(request):
    if request.method == 'POST':
        xn = request.POST['xn']
        xq = request.POST['xq']
        classCode = request.POST['classCode']
        userCode = request.POST['userCode']
        sjxz = "sjxz3"
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.getClassGrade(xn, xq, sjxz, userCode,classCode)
        return HttpResponse(res)
    else:
        xn = request.GET['xn']
        xq = request.GET['xq']
        classCode = request.GET['classCode']
        userCode = request.GET['userCode']
        sjxz = "sjxz3"
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.getClassGrade(xn, xq, sjxz, userCode,classCode)
        return HttpResponse(res)


@csrf_exempt
def getUserByName(request):
    if request.method == 'POST':
        db = pymysql.connect("localhost","root","","login",charset='utf8' )
        cursor = db.cursor() 
        # cursor2 = db.cursor()
        name = request.POST['name']
        like=name+'%'
        sql="select * from wechat_data where username like '"+like+"'"   
        cursor.execute(sql)
        results = cursor.fetchall()    #获取查询的所有记录
        result={}
        lis=[]  
        for row in results:  
            dic={}
            dic["usercode"]=row[1][0:11]
            dic["username"]=row[2]
            dic["usersex"]=row[3]
            dic["usermajor"]=row[5]
            lis.append(dic)
        db.close()
        result["data"]=lis
        return HttpResponse(json.dumps(result))
    else:
        db = pymysql.connect("localhost","root","","login",charset='utf8' )
        cursor = db.cursor() 
        # cursor2 = db.cursor()
        name = request.GET['name']
        like=name+'%'
        sql="select * from wechat_data where username like '"+like+"'"   
        cursor.execute(sql)
        results = cursor.fetchall()    #获取查询的所有记录
        result={}
        lis=[]  
        for row in results:  
            dic={}
            dic["usercode"]=row[1][0:11]
            dic["username"]=row[2]
            dic["usersex"]=row[3]
            dic["usermajor"]=row[5]
            lis.append(dic)
        db.close()
        result["data"]=lis
        return HttpResponse(json.dumps(result))


@csrf_exempt
def getClassCode(request):
    if request.method == 'POST':
        xn = request.POST['xn']
        xq = request.POST['xq']
        classtype = request.POST['classtype']
        classname = request.POST['classname']
        classname=urllib.parse.unquote(classname)
        res = oucjw.getClassCode(xn, xq, classtype, classname)
        return HttpResponse(res)
    else:
        xn = request.GET['xn']
        xq = request.GET['xq']
        classtype = request.GET['classtype']
        classname = request.GET['classname']
        classname=urllib.parse.unquote(classname)
        res = oucjw.getClassCode(xn, xq, classtype, classname)
        return HttpResponse(res)



@csrf_exempt
def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        global oucjw
        res = oucjw.login(username,password)
        # print(oucjw.login('15020031106', '19961020.zqx+-')
        return HttpResponse(res)
    else:
        username = request.GET['username']
        password = request.GET['password']
        global oucjw
        # print(oucjw.login('15020031106', '19961020.zqx+-'))
        res = oucjw.login(username,password)
        return HttpResponse(res)