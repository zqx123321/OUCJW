from .BaseOucJw import BaseOucJw
import re
import base64
import json


class OucJw(BaseOucJw):

    def __init__(self):
        BaseOucJw.__init__(self)

    def getUserCode(self, xn, xq, classCode):
        if(xq=='2'):
            xn=str(int(xn)-1)
        refer = self.HOST + 'common/popmsg/popmsg.sendOnlineMessage.jsp'
        url = self.HOST + 'taglib/DataTable.jsp?tableId=3241&type=skbjdm'
        postdic = {
            'xnxq': xn + '-' + xq,
            'sel_skbjdm': classCode,
        }
        content = self.opener.post(url, postdic, {'Referer': refer})
        res = r'<td .*?>(.*?)</td>'
        mm = re.findall(res, content, re.S | re.M)
        lis = []
        for i in range(1, len(mm)):
            if (9 * i) + 5 > len(mm) or (9 * i) + 5 == len(mm):
                break
            dic = {}
            dic["usercode"] = mm[9 * i + 1]
            dic["username"] = mm[9 * i + 2]
            dic["usersex"] = mm[9 * i + 3]
            dic["userfaculty"] = mm[9 * i + 4]
            dic["usermajor"] = mm[9 * i + 5]
            lis.append(dic)
        result = {}
        result["students"] = lis
        return json.dumps(result)

    def getGrade(self, xn, xq, sjxz, userCode):
        try:
            if(xq=='2'):
                xn=str(int(xn)-1)
            refer = self.HOST + 'student / xscj.stuckcj.jsp?menucode = JW130705'
            param = 'xn=' + xn + '&xn1=' + xn + '&xq=' + xq + '&ysyx=yscj&sjxz=' + sjxz + '&userCode=' + userCode[0:11]
            token = self.getKeytoken()
            data = self.encodeParam(param, token)
            url = self.HOST + 'student/xscj.stuckcj_data.jsp'
            content = self.opener.get(url, data, {'Referer': refer})
            name = re.findall(r'<div style="float:left;text-align:left;width: 20%;">(.+?)</div>', content)[0]
            result = {}
            result["name"] = name.replace("姓名：", "")
            lis = []
            className = re.findall(r'](.+?)</td>', content)
            mm = re.findall(r'<td style="text-align: right;">(.+?)</td>', content)
            for i in range(0, len(mm)):
                if i % 2 == 1:
                    dic = {}
                    dic["classname"] = className[int(i / 2)]
                    dic["score"] = mm[i - 1]
                    dic["grade"] = mm[i]
                    lis.append(dic)
                    continue
            calc = self.calcGrade(lis)
            result["data"] = lis
            result["score"] = calc["score"]
            result["average"] = calc["average"]
            return json.dumps(result)
        except:
            result = {}
            result["name"] = ""
            lis = []
            dic = {}
            dic["classname"] = ""
            dic["score"] = 0
            dic["grade"] = 0
            lis.append(dic)
            result["data"] = lis
            result["score"] = 0
            result["average"] = 0
            return json.dumps(result)


    def getClassName(self, xn, xq, userCode, classCode):
        if(xq=='2'):
            xn=str(int(xn)-1)
        refer = self.HOST + 'student/xkjg.wdkb.jsp?menucode=JW130416'
        url = self.HOST + 'wsxk/xkjg.ckdgxsxdkchj_data.jsp'
        params = ('xn=' + xn + '&xq=' + xq + '&xh=' + userCode[0:11])[0:27]
        line = base64.b64encode(params.encode('utf-8'))
        line = str(line, 'utf-8')
        values = {
            'params': line,
        }
        content = self.opener.get(url, values, {'Referer': refer})
        classcode = re.findall(r'<td style="text-align:center;">(.+?)</td>', content)
        classname = re.findall(r'<td style="text-align:left;">(.+?)]', content)

        for i in range(0, int(len(classcode) / 6)):
            if classcode[6 * i] == classCode:
                return classname[3 * i][1:len(classname[3 * i])]
        return ''

    def getClassGrade(self, xn, xq, sjxz, userCode, classCode):
        if(xq=='2'):
            xn=str(int(xn)-1)
        refer = self.HOST + 'student / xscj.stuckcj.jsp?menucode = JW130705'
        param = 'xn=' + xn + '&xn1=' + xn + '&xq=' + xq + '&ysyx=yscj&sjxz=' + sjxz + '&userCode=' + userCode[0:11]
        token = self.getKeytoken()
        data = self.encodeParam(param, token)
        url = self.HOST + 'student/xscj.stuckcj_data.jsp'
        content = self.opener.get(url, data, {'Referer': refer})

        className = re.findall(r'<td>\[(.+?)]', content)
        mm = re.findall(r'<td style="text-align: right;">(.+?)</td>', content)
        result = {}
        for i in range(0, len(mm)):
            if i % 2 == 1:
                if className[int(i / 2)] == classCode:
                    result["score"] = mm[i]
                    return json.dumps(result)
        result["score"] = -1
        return json.dumps(result)

    def getClassCoin(self, xn, xq, classCode, userCode):
        try:
            if(xq=='2'):
                xn=str(int(xn)-1)
            refer = self.HOST + 'student / xscj.stuckcj.jsp?menucode = JW130705'
            url = self.HOST + 'wsxk/xkjg.ckdgxsxdkchj_data.jsp'

            params = ('xn=' + xn + '&xq=' + xq + '&xh=' + userCode[0:11])[0:27]
            line = base64.b64encode(params.encode('utf-8'))
            line = str(line, 'utf-8')
            values = {'params': line}
            content = self.opener.get(url, values, {'Referer': refer})
            res = r'<td .*?>(.*?)</td>'
            mm = re.findall(res, content, re.S | re.M)
            result = {}
            for i in range(1, 100000):
                if (15 * i + 5) > len(mm) or (15 * i + 5) == len(mm):
                    break
                if (mm[15 * i - 4] == classCode):
                    result["coin"] = mm[15 * i + 4]
                    return json.dumps(result)
            result["coin"] = -1
            return json.dumps(result)
        except:
            result = {}
            result["coin"] = -1
            return json.dumps(result)


    def getClassTable(self, xn, xq, userCode):
        if(xq=='2'):
            xn=str(int(xn)-1)
        url = self.HOST + 'student/wsxk.xskcb.jsp'
        refer = self.HOST + 'student/xkjg.wdkb.jsp?menucode=JW130416'
        params = ('xn=' + xn + '&xq=' + xq + '&xh=' + userCode[0:11])[0:27]
        line = base64.b64encode(params.encode('utf-8'))
        line = str(line, 'utf-8')
        values = {
            'params': line,
        }
        result = {}
        content = self.opener.get(url, values, {'Referer': refer})
        for i in range(1, 8):
            for j in range(1, 6):
                result[str(i) + str(j)] = ''
                mm = re.findall(r"<div class='.*' id='k" + str(i) + str(j) + "'>(.+?)</td>", content, re.S | re.M)
                for k in mm:
                    if k.find("未选中") != -1:
                        continue
                    rr = re.findall(r"<div style='padding-bottom:5px;clear:both;'>(.+?)</div>", k, re.S | re.M)
                    if len(rr) > 0:
                        info = rr[0].replace("<b>", "").replace("</b><br>", " ").replace("&nbsp;", " ").replace("*",
                                                                                                                "").replace(
                            "  ", " ")
                        result[str(i) + str(j)] = info
        return json.dumps(result)

    def calcGrade(self, grades):
        rules = {
            "优秀": 90, "良好": 80, "中等": 70, "合格": 60, "不合格": 0, "通过": 60, "不通过": 0
        }
        data = {}
        s = 0
        total = 0
        score = 0
        result = {}
        for i in grades:
            # 成绩转换
            try:
                s = float(i["grade"])
            except:
                s = rules[i["grade"]]
            score += float(i["score"])
            t = s * float(i["score"])
            if (i["classname"] in data.keys()):
                # 判断刷分
                if (t > data[i["classname"]]):
                    data[i["classname"]] = t
                    score -= float(i["score"])
            else:
                data[i["classname"]] = t

        for key in data:
            total += data[key]

        result["score"] = score
        result["average"] = total / score
        return result

    def getClassTable2(self,xn,xq,userCode):
        if(xq=='2'):
            xn=str(int(xn)-1)
        url=self.HOST+'student/wsxk.xskcb.jsp'
        refer=self.HOST+'student/xkjg.wdkb.jsp?menucode=JW130416'
        params=('xn='+xn+'&xq='+xq+'&xh='+userCode[0:11])[0:27]
        line=base64.b64encode(params.encode('utf-8'))
        line=str(line,'utf-8')
        values={
            'params':line,
        }
        result=[]
        content = self.opener.get(url, values, {'Referer':refer})
        for i in range(1,8):
            lis=[]
            for j in range(1,6):
                mm=re.findall(r"<div class='.*' id='k"+str(i)+str(j)+"'>(.+?)</td>", content, re.S|re.M)
                for k in mm:
                    if k.find("未选中")!=-1:
                        continue
                    rr=re.findall(r'''<span class="xkinfo">(.+?)</span>''', k, re.S|re.M)
                    if len(rr)>0:
                        rr[0]=rr[0].replace("<div style='padding-bottom:5px;clear:both;'>","").replace("</div>","")
                        temp={}
                        templ=[]
                        info=rr[0].replace("<b>","").replace("</b><br>"," ").replace("&nbsp;"," ").replace("*","").replace("  "," ")
                        infos=info.split(' ')
                        temp["name"]=infos[0]
                        temp["teacher"]=infos[1]
                        temp["detail"]=info
                        templ.append(temp)
                        lis.append(templ)
                    else:
                        templ=[]
                        lis.append(templ)
            result.append(lis)
        return json.dumps(result)



    def getClassCode(self,xn,xq,classtype,classname):
        try:
            if(xq=='2'):
                xn=str(int(xn)-1)
            refer=self.HOST+'student/wsxk.kcbcx.html?menucode=JW130414'
            url=self.HOST+'taglib/DataTable.jsp?tableId=6146'
            postData='xn='+xn+'&xq='+xq+'&zydm=0011&kcfw='+classtype+'&sel_zydm=0011&sel_kc='+classname
            content = self.opener.post(url, postData, {'Referer':refer},isChange=1)
            code=re.findall(r"<td id='tr._curent_skbjdm' name='curent_skbjdm'  align='center' >(.*?)</td>", content, re.S|re.M)
            name=re.findall(r"](.*?)</a>", content, re.S|re.M)
            teacher=re.findall(r"<td id='tr._rkjs' name='rkjs'  align='left' >(.*?)</td>", content, re.S|re.M)
            rteacher=[]
            result={}
            rcode=[]
            lis=[]
            for i in code:
                if(len(i)>0):
                    rcode.append(i)
            for i in teacher:
                if(len(i)>0):
                    rteacher.append(i)
            for i in range(0,len(rcode)):
                dic={}
                dic["name"]=name[i]
                dic["teacher"]=rteacher[i]
                dic["code"]=rcode[i]
                lis.append(dic)
            result["data"]=lis
            return json.dumps(result)
        except:
            dic={}
            dic["name"]=""
            dic["code"]=""
            lis=[]
            lis.append(dic)
            result={}
            result["data"]=lis
            return json.dumps(result)
