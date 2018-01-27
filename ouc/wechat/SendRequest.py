# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import http.cookiejar
import socket
import chardet
class SendRequest():
	"""docstring for SendRequest"""
	def __init__(self,timeout = 30,addheaders = True):
		socket.setdefaulttimeout(timeout)
		self.__opener = urllib.request.build_opener()
		if addheaders:self.__addHeaders()

	def __error(self,e):
		print(e)

	def __decode(self,html):
		char = chardet.detect(html)
		data = html.decode(char['encoding'],'ignore')
		return data

	def __addHeaders(self):
		self.__opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'), 
		('Connection', 'keep-alive')]

	def addCookiejar(self):
		cj = http.cookiejar.CookieJar()
		self.__opener.add_handler(urllib.request.HTTPCookieProcessor(cj))

	def addProxy(self,host,type = 'http'):
		proxy = urllib.request.ProxyHandler({type:host})
		self.__opener.add_handler(proxy)

	def get(self, url, params={}, headers={}, charset='gbk'):  
		'''''HTTP GET 方法'''  
		if params: url += '?' + urllib.parse.urlencode(params)  
		request = urllib.request.Request(url)  
		for k,v in headers.items(): request.add_header(k, v)    # 为特定的 request 添加指定的 headers  
		try:  
			response = self.__opener.open(request)  
		except urllib.error.HTTPError as e:  
			self.__error(e)  
		else:
			return self.__decode(response.read())

	def post(self, url, params={}, headers={}, charset='gbk',isChange=0):  
		'''''HTTP POST 方法'''  
		if isChange==0:
			params = urllib.parse.urlencode(params)  

		request = urllib.request.Request(url, data=params.encode(charset))  # 带 data 参数的 request 被认为是 POST 方法。  
		for k,v in headers.items(): request.add_header(k, v)  
		
		try:  
			response = self.__opener.open(request)  
		except urllib.error.HTTPError as e:  
			self.__error(e)  
		else:  
			return self.__decode(response.read())
	def getCode(self,url,headers = {}):
		request = urllib.request.Request(url)
		for k,v in headers.items():request.add_header(k,v)

		try:
			response =urllib.request.urlopen(request)
			return response.code
		except Exception as e:
			return e
