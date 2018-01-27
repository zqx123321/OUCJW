# -*- coding: utf-8 -*-
from .DES import *
import re
import base64
import urllib.request
import http.cookiejar
from .SendRequest import SendRequest
class BaseOucJw():
	"""docstring for OucJw"""
	def __init__(self):
		self.opener = SendRequest()
		self.opener.addCookiejar()
		self.testURL()


	def testURL(self):
		self.url = ['http://222.195.158.225/oucjw/','http://jwgl2.ouc.edu.cn/','http://jwgl.ouc.edu.cn/','http://222.195.158.206/oucjw/']
		for x in self.url:
			code = self.opener.getCode(x+"cas/login.action")
			if(code == 200):
				self.HOST =  x
				break
			else:
				print(code)

	def setProxy(self,proxy):
		pass

	def setUser(self,username,password):
		self.username = username
		self.password = password

	def md5HashPasswd(self,passwd, verify):
		return get_md5_value(get_md5_value(passwd) + get_md5_value(verify.lower()))

	def getKeytoken(self):
		url = self.HOST + 'custom/js/SetKingoEncypt.jsp'
		content = self.opener.get(url,{})
		d = re.findall("= (.+);",content)
		_deskey = d[0].replace('\'','')
		_nowtime = d[1].replace('\'','')
		data = {'_deskey':_deskey,'_nowtime':_nowtime}
		return data

	def encodeParam(self,param,token):
		result =getEncParams(param,token['_nowtime'],token['_deskey'])
		result['timestamp'] = token['_nowtime']
		return result

	def getSessionId(self):
		text = self.opener.get(self.HOST + "cas/login.action")
		self.sessionid = re.findall("= (.+);",text)[1].replace('"','')

	def login(self,username,password,verify =''):
		self.getSessionId()
		self.setUser(username,password)
		u = base64.b64encode((username+";;"+self.sessionid).encode(encoding="gbk")).decode(encoding="gbk")
		p_username = "_u"+verify;
		p_password = "_p"+verify;
		data = {
		    p_username: u,
		    p_password: self.md5HashPasswd(password, verify),
		    'randnumber': verify,
		    'isPasswordPolicy': '1'
		}
		url = self.HOST + 'cas/logon.action'
		data = self.opener.post(url,data)
		return data






