

from django.conf.urls import include, url
from wechat.views import *

urlpatterns=[
    url(r'^$', handleRequest),
    url(r'^getGrade/$',getGrade,name="getGrade"),
    url(r'^login/$',login,name="login"),
    url(r'^bind/$',bind,name="bind"),
    url(r'^getUserCode/$',getUserCode,name="getUserCode"),
    url(r'^getClassName/$',getClassName,name="getClassName"),
    url(r'^getUserCoin/$',getUserCoin,name="getUserCoin"),
    url(r'^getMajor/$',getMajor,name="getMajor"),
    url(r'^getUser/$',getUser,name="getUser"),
    url(r'^getClassTable/$',getClassTable,name="getClassTable"),
    url(r'^getClassGrade/$',getClassGrade,name="getClassGrade"),
    url(r'^unbind/$',unbind,name="unbind"),
    url(r'^getUserByName/$',getUserByName,name="getUserByName"),
    url(r'^getClassCode/$',getClassCode,name="getClassCode"),
    url(r'^Login/$',Login,name="Login"),
]
