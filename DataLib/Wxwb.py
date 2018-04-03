from bs4 import BeautifulSoup,NavigableString
import urllib.request as urlRequest
import urllib.parse as urlParse
import os
import configparser
import datetime
import re
import time
import json
import requests
import base64
import rsa
import binascii
import random
import traceback
import jieba
import jieba.analyse

from threading import Thread as thread
import threading
class wxwb(thread):
    def __init__(self, file, conn):
        thread.__init__(self)
        self.configFile = file
        self.session = requests.Session()
        self.conn = conn
        self.exception = None
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()
        self.coockie="IPLOC=CN4201; SUID=0499C5DA2028940A000000005A6D4B75; SUID=E0B0AC3B2513910A000000005A6D4B76; weixinIndexVisited=1; SUV=00DE5AA43BACB0E05A6D4B77ABF4C088; ABTEST=0|1522336708|v1; SNUID=144558CEF4F09D044E7A484CF5BC576F; JSESSIONID=aaay89FYM96oI_Cb4KOiw; ppinf=5|1522763746|1523973346|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo2OllhbmFubnxjcnQ6MTA6MTUyMjc2Mzc0NnxyZWZuaWNrOjY6WWFuYW5ufHVzZXJpZDo0NDpvOXQybHVKQTNpUllKRi1yVXEzbDNMWGpmazBVQHdlaXhpbi5zb2h1LmNvbXw; pprdig=s3F4d-BqKeaMBhgTh4InXef39OFN8I3rvdxGHLhjlXeK7NraJVdYG6R0QR0zDRQMyLtERJvsm_fldEkVyP_sPtENWUZ23_BlRNHdPgaExiaxk8AeXTBEXgc7s_-r_NEbpqK6LjIjU3DL-L_m0BV_q9iP8A0UQEuT-EcpHweH568; sgid=07-31103317-AVrDhibLQnuo2t6fA4IoRficE; sct=13; ppmdig=152276689100000063552a5377d042fad92db2cce572928e"

    def pause(self):
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def stop(self):
        self.__flag.set()
        self.__running.clear()
    def timeSleep(self):
        self.conn.saveLogInfo("wxwb", "微信验证码出现，稍后抓取",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微信验证码出现，稍后抓取   " + "运行状态: " + str(1))
        time.sleep(3600)
    ## 微信搜狗接口,初始化过程爬取一年的时间
    def wx(self,type):
        self.conn.saveLogInfo("wxwb", "正在抓取微信信息", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "正在抓取微信信息   " + "运行状态: " + str(1))
        tsn = 1
        referUrlHead = None
        referUrlBottom = None
        urlHead = None
        urlBottom = None

        if type == 0:
            tsn = 3
        if type == 1:
            tsn = 1
        if type == 2:
            referUrlHead = "http://weixin.sogou.com/weixin?type=2&s_from=input&query="
            referUrlBottom = "&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=1278&sst0=1522764396636&lkt=1%2C1522764396534%2C1522764396534"

            endTime = time.strftime("%Y-%m-%d")
            startTime = datetime.datetime.now() - datetime.timedelta(days = 120)
            startTime = startTime.strftime("%Y-%m-%d")

            urlHead = "http://weixin.sogou.com/weixin?type=2&ie=utf8&query="
            urlBottom = "&tsn=5&ft=" + startTime +"&et=" + endTime

        self.addresses, self.keyList = self.conn.getWxWbKey("weixin")
        for i,keys in enumerate(self.keyList):
            self.keysList = keys.split("|")[0].strip(" ")
            self.keysScapes = keys.split("|")[1].strip(" ")
            page = 1
            liLen = 0
            queryKeys = self.addresses[i] + " " + keys.split("|")[0].strip(" ")
            reKey = queryKeys.replace(" ","+")

            if urlHead:
                referUrlInit = referUrlHead + urlParse.quote(reKey) + referUrlBottom
            else:
                referUrlInit = "http://weixin.sogou.com/weixin?type=2&query="+ urlParse.quote(reKey) +"&ie=utf8&s_from=input&_sug_=y&_sug_type_=&w=01015002&oq=%E5%A4%A7%E7%90%86+&ri=0&sourceid=sugg&stj=0%3B0%3B0%3B0&stj2=0&stj0=0&stj1=0&hp=32&hp1=&sut=3012&sst0=1522390441307&lkt=2%2C1522390439917%2C1522390441204"
            while True:
                if urlHead:
                    if page == 1:
                        url = urlHead + urlParse.quote(queryKeys) + urlBottom + "&interation=&wxid=&usip="
                    else:
                        url = "http://weixin.sogou.com/weixin?usip=&query=" +urlParse.quote(reKey)+ urlBottom + "&interation=&type=2&wxid=&page=2&ie=utf8"
                else:
                    if page == 1:
                        url = "http://weixin.sogou.com/weixin?type=2&ie=utf8&query"+urlParse.quote(queryKeys)+"=&tsn="+ str(tsn) +"&ft=&et=&interation=&wxid=&usip="
                    else:
                        url = "http://weixin.sogou.com/weixin?usip=&query="+urlParse.quote(queryKeys)+"&ft=&tsn="+ str(tsn) +"&et=&interation=&type=2&wxid=&page="+str(page)+"&ie=utf8"
                head = {"Host":"weixin.sogou.com",
                        "Accept-Encoding":"gzip, deflate",
                        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                        "Cookie":self.coockie,
                        "Referer":referUrlInit}
                res = requests.get(url,headers=head).content
                soup = BeautifulSoup(res,"lxml")
                if soup.find("p",{"class":self.wxIpClass}):
                    self.timeSleep()
                    continue
                ulContent = soup.find("ul",{"class":self.wxUlListClass})
                if not ulContent:
                    print("len"+str(liLen))
                    break
                liList = ulContent.findAll("li")
                liLen += len(liList)
                for li in liList:
                    txtDiv = li.find("div", {"class": self.wxDivTxt})
                    titleA = txtDiv.find("h3").find("a")
                    comment = titleA.text + txtDiv.find("p").text
                    articalHerf = titleA["href"]
                    nickDiv = txtDiv.find("div", {"class": self.wxNickDiv})
                    if not self.analyze(articalHerf,nickDiv.find("a").text,None):
                        self.conn.saveLogInfo("wxwb", articalHerf + "该文章不符合要求", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),1)
                        print("wxwb "+ articalHerf + "该微信文章不符合要求" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + str(1))
                        continue


                    imgs = li.findAll("img")
                    imgList = list()
                    if imgs:
                        for img in imgs:
                            imgList.append(img["src"])
                    imgStr = "{"
                    if imgList:
                        for img in imgList:
                            imgStr += img+","
                        imgStr = imgStr[0:len(imgStr)-1]+"}"
                    sqlDict = dict()
                    sqlDict["nick"] = nickDiv.find("a").text
                    ymTime = re.findall("\(\'(.*?)\'\)",nickDiv.find("span").text)
                    if len(ymTime) <= 0:
                        continue
                    time_local = time.localtime(int(ymTime[0]))
                    dtime = time.strftime('%Y-%m-%d %H:%M:%S', time_local)
                    sqlDict["dtime"] = dtime
                    sqlDict["comment"] = comment.replace("'"," ")
                    sqlDict["href"] = articalHerf
                    if imgStr == "{":
                        sqlDict["img"] = "{}"
                    else:
                        sqlDict["img"] = imgStr
                    self.conn.saveWxWb(sqlDict,"media.weixin")
                pageDiv = soup.findAll("div",{"class":self.wxPageDiv})
                if len(pageDiv) == 0:
                    break
                if type == 1:
                    time.sleep(random.randint(10,20))
                if type == 0 :
                    self.conn.saveLogInfo("wxwb", "微信初始化一个月防验证码sleep",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print("wxwb " + "微信初始化一个月防验证码sleep" + datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S") + str(1))
                    time.sleep(1000)
                if type == 2 :
                    self.conn.saveLogInfo("wxwb", "微信初始化四个月防验证码sleep",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print("wxwb " + "微信初始化四个月防验证码sleep" + datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S") + str(1))
                    time.sleep(1000)
                page += 1
                referUrlInit = url
            if liLen == 0 :
                self.conn.saveLogInfo("wxwb", self.addresses[i] + "微信未抓取到任何记录，请检查是否出错", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + self.addresses[i] + " 微信未抓取到任何记录，请检查是否出错   " + "运行状态: " + str(1))



    # def notKeySacape(self,str):
    #     lists = self.keysScapes.split(" ")
    #     for keyscape in lists:
    #         result = re.findall(keyscape,str)
    #         if len(result) > 0:
    #             return False
    #     lists = self.keysList.split(" ")
    #     result = re.findall(lists[0],str)
    #     if len(result) == 0:
    #         return False
    #     return True

    def wb(self,week):
        self.conn.saveLogInfo("wxwb", "正在抓取微博信息", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "正在抓取微博信息   " + "运行状态: " + str(1))
        try:
            servertime, nonce, rsakv, pubkey = self.get_logininfo()
        except:
            return
        postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'savestate': '7',
            'userticket': '0',
            "vsnf": "1",
            "su": self.get_user(self.wbAccount),
            "service": "miniblog",
            "servertime": servertime,
            "nonce": nonce,
            "pwencode": "rsa2",
            "rsakv": rsakv,
            "sp": self.get_sp(servertime,nonce,pubkey),
            "sr": "1366*768",
            "encoding": "UTF-8",
            "prelt": "282",
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META",
        }
        url = r'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        session = self.wbLogin(postdata, url)
        if session:
            self.addresses, self.keyList = self.conn.getWxWbKey("weibo")
            for i,keys in enumerate(self.keyList):
                self.keysScapes = keys.split("|")[1].strip(" ")
                self.keysList = keys.split("|")[0].strip(" ")
                self.spiderWb(session,self.addresses[i]+ " "+ keys.split("|")[0],week)
    def wbLogin(self,postdata,url):
        session = requests.session()
        res = session.post(
                url=url,
                data=postdata
            )
        html = str(res.content, encoding="gbk")
        info = re.findall("location\\.replace\\(\\'(.*?)\\'\\)", html)[0]
        login_index = session.get(info)
        login_res = login_index.text
        errorReason = re.findall('reason=(.*?)\\"', login_res)
        if len(errorReason) > 0:
            self.conn.saveLogInfo("wxwb", "微博登陆失败，原因是：%s"%errorReason[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微博登陆失败，原因是：%s   "%errorReason[1] + "运行状态: " + str(1))
            return None
        else:
            self.conn.saveLogInfo("wxwb", "微博登陆成功",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微博登陆成功  "+ "运行状态: " + str(1))
            return session
    def spiderWb(self,session,keyword,weeks):

        # 搜索网页
        self.conn.saveLogInfo("wxwb", "开始抓取微博", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "开始抓取微博  " + "运行状态: " + str(1))
        keyword = urlRequest.quote(keyword)
        pam = "&typeall=1&suball=1&timescope=custom:"

        testUrl = "http://s.weibo.com/weibo/"+keyword+pam+self.getTime(weeks)+"&Refer=g"
        res = session.get(testUrl)
        if not res:
            self.conn.saveLogInfo("wxwb", "微博查询结果为空", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微博查询结果为空  " + "运行状态: " + str(1))
            return
        content = res.text
        test = re.findall('<script>STK && STK\\.pageletM && STK\\.pageletM\\.view\\((.*)\\)</script>', content)
        body = None
        for jsonStr in test:
            testJson = json.loads(jsonStr)
            if testJson["pid"] != "pl_weibo_direct":
                continue
            body = testJson["html"]
            break
        assert body
        soup = BeautifulSoup(body,"lxml")
        searchContent = soup.find("div",{"class":self.webDivSearch})
        noResult = searchContent.find("div",{"class":self.webDivNoResult})
        if noResult:
            self.conn.saveLogInfo("wxwb", "微博未找到相关结果", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微博未找到相关结果  " + "运行状态: " + str(1))
            return

        divList = searchContent.findAll("div",{"class":self.webDivClass})
        faceList = searchContent.findAll("div",{"class":self.webDivFace})
        length = 0
        for div in divList:
            ## 移除转发原文
            originArticle = div.find("div",{"class":self.webDivOrigin})
            if originArticle:
                originArticle.decompose()

            resultDict = dict()
            name =  div.find("a",{"class":self.webAcontentClass})
            nick = name["nick-name"]
            comment = div.find("p",{"class":self.webPcommentClass}).text
            concretContent = div.find("a", {"class": self.webAconcretClass})
            href = concretContent["href"]
            ## 加入筛选机制
            if not self.analyze("http:" + href,nick,session):
                self.conn.saveLogInfo("wxwb", "http:"+ href+ "该文章不符合要求", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print("wxwb " + "http:"+ href + "该微信文章不符合要求" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + str(1))
                continue

            # if not self.notKeySacape(conment):
            #     continue
            time = concretContent["title"]
            ulMedia = div.find("ul")
            imageListStr = ""
            if ulMedia:
                for li in ulMedia.findAll("li"):
                    imageListStr += re.findall("\//(.*)",li.find("img")["src"])[0]+","
                imageListStr = imageListStr[0:len(imageListStr)-1]
            faceSrc = re.findall("\//(.*)",faceList[length].find("img")["src"])[0]
            length += 1
            resultDict["face"] = faceSrc
            icon = name.nextSibling
            while isinstance(icon,NavigableString):
                icon = icon.nextSibling
            resultDict["class"]=0
            # for classStr in icon["class"]:
            #     if classStr.find("aprove") >= 0:
            #         resultDict["class"]=1
            #         break
            loc=div.find("a",{"class":self.webLocClass})
            lat, lon = "",""
            if loc:
                if re.match("http:\//t\.cn\/",loc["href"]):
                    lat,lon = self.requestLatLon(loc["href"])
            resultDict["lat"] = lat
            resultDict["lon"] = lon
            resultDict["nick"] = nick
            resultDict["comment"] = comment
            resultDict["href"] ="http:"+href
            resultDict["dtime"]=time
            resultDict["img"] = "{"+imageListStr+"}"
            resultDict["filePath"] = ""

            self.conn.saveWxWb(resultDict,"media.weibo")
    def requestLatLon(self,url):
        res = requests.request("GET",url)
        matchResult = re.findall("\$CONFIG\[\'oid\'\]=\'(.*)\'",res.text)
        if len(matchResult) > 0:
            strT = matchResult[1].split("_")
            if len(strT) >= 2:
                return str(strT[1]),str(strT[0])
        return "",""

    def get_logininfo(self):
        nowTime = lambda: int(round(time.time() * 1000))
        preLogin_url = r'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&' \
                        r'su=&rsakt=mod&client=ssologin.js(v1.4.15)&_='+ str(nowTime())
        html = requests.get(preLogin_url).text
        jsonStr = re.findall('\\((.*?)\\)', html)[0]
        data = json.loads(jsonStr)
        servertime = data["servertime"]
        nonce = data["nonce"]
        pubkey = data["pubkey"]
        rsakv = data["rsakv"]
        return servertime, nonce, rsakv,pubkey
    def get_user(self, username):
        username_ = urlParse.quote(username)
        username = base64.encodebytes(bytes(username_, encoding="utf-8"))[:-1]
        return str(username, encoding="utf-8")
    def get_sp(self, servertime, nonce, pubkey):
        pubkey = int(pubkey, 16)
        key = rsa.PublicKey(pubkey, 65537)
        # 以下拼接明文从js加密文件中得到
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(self.wbPassword)
        message = bytes(message,encoding="utf-8")
        sp = rsa.encrypt(message, key)
        # 把二进制数据的每个字节转换成相应的2位十六进制表示形式。
        sp = binascii.b2a_hex(sp)
        return sp
    def getTime(self,week):
        time = datetime.datetime.now()
        preTime = time - datetime.timedelta(weeks=week)
        time = time.strftime("%Y-%m-%d")
        preTime = preTime.strftime("%Y-%m-%d")
        return preTime+":"+time

    def loadConf(self):
        self.conn.saveLogInfo("wxwb", "读取微博微信配置文件", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "读取微博微信配置文件  " + "运行状态: " + str(1))
        conf = configparser.ConfigParser()
        conf.read(self.configFile, "utf-8")
        self.wbAccount = conf.get(conf.sections()[1], "username")
        self.wbPassword = conf.get(conf.sections()[1], "password")

        # 微博字段
        self.webDivSearch=conf.get(conf.sections()[2],"divSearch")
        self.webDivClass=conf.get(conf.sections()[2],"divClass")
        self.webDivNoResult=conf.get(conf.sections()[2],"divNoReusltClass")
        self.webAcontentClass=conf.get(conf.sections()[2],"aContentClass")
        self.webPcommentClass=conf.get(conf.sections()[2],"pCommentClass")
        self.webAconcretClass=conf.get(conf.sections()[2],"aConcretClass")
        self.webDivFace=conf.get(conf.sections()[2],"divFace")
        self.webLocClass=conf.get(conf.sections()[2],"aLocClass")
        self.webDivOrigin = conf.get(conf.sections()[2],"divOriginClass")

        # 微信字段
        self.wxDivTxt = conf.get(conf.sections()[3],"divTxtBox")
        self.wxNickDiv = conf.get(conf.sections()[3],"nickDiv")
        self.wxIpClass=conf.get(conf.sections()[3],"ipClass")
        self.wxUlListClass = conf.get(conf.sections()[3],"ulListClass")
        self.wxPageDiv = conf.get(conf.sections()[3],"pageDiv")

    ## 每天晚上9点抓取一次
    def run(self):
        self.conn.saveLogInfo("wxwb", "微信微博线程开始", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微信微博线程开始  " + "运行状态: " + str(1))
        try:
            while self.__running.isSet():
                self.__flag.wait()
                hour = datetime.datetime.now().hour
                if hour == 21:
                    self.wx(type=1)
                    self.conn.saveLogInfo("wxwb", "微信一天信息抓取完毕", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微信一天信息抓取完毕  " + "运行状态: " + str(1))
                    self.wb(1)
                    self.conn.saveLogInfo("wxwb", "微博一天信息抓取完毕", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微博一天信息抓取完毕  " + "运行状态: " + str(1))
                time.sleep(3600)
        except Exception as e:
            traceback.print_exc()
            self.exception = e
            self.exTrace = traceback.format_exc()
    def getException(self):
        if self.exception:
            exString = ""
            for arg in self.exception.args:
                exString += str(arg)
            if not self.exTrace:
                exString += self.exTrace
            exString = exString.replace("'", "")
            self.conn.saveLogInfo("wxwb", "微信微博线程异常%s"%exString, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微信微博线程异常%s   "%exString + "运行状态: " + str(0))
        else:
            self.conn.saveLogInfo("wxwb", "微信微博线程异常：异常结果为空", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微信微博线程异常：异常结果为空  " + "运行状态: " + str(0))
    def dbReset(self,db):
        self.conn = db

    ## 提取文章中出现最多的5个词频
    ## 依次判断是否存在关键词
    ## 首先判断是否存在位置关键词，继而判断是否存在污染关键词
    def analyze(self,artical_url,nickName,session):
        text = None
        if session == None:
            request = urlRequest.Request(artical_url)
            response = urlRequest.urlopen(request)
            if response.status != 200:
                return False
            soup = BeautifulSoup(response, "lxml")
            text = soup.text
        else:
            response = session.get(artical_url).text
            jsonDetil = re.findall('(\{"ns"\:"pl\.content\.weiboDetail\.index".*?\})\)\<\/script\>',response)
            if len(jsonDetil) <= 0:
                return False
            data = json.loads(jsonDetil[0])
            html = data["html"]
            soup = BeautifulSoup(html, "lxml")
            text = soup.find("div",{"class":"WB_text W_f14"}).text
        pattern = '[\u4e00-\u9fff]+'
        re_compile = re.compile(pattern)
        chList = re_compile.findall(text)
        if len(chList) == 0:
            return False
        chRes = "".join(chList)

        if session != None:
            if len(chRes) > 400:
                tags = jieba.analyse.extract_tags(chRes, topK=15)
                return self.wxKeyAnalyze(tags, nickName)
            else:
                return self.wbKeyAnalyze(chRes)
        else:
            tags = jieba.analyse.extract_tags(chRes, topK=8)
            return self.wxKeyAnalyze(tags, nickName)



    def wxKeyAnalyze(self,keyTags,nickName):
        addressFlag = False
        nickNameList = " ".join(jieba.cut(nickName,cut_all=False)).split(" ")
        ## 判断位置是否正确
        for keyTag in keyTags:
            for address in self.addresses:
                if len(re.findall(address, keyTag)) > 0:
                    addressFlag = True
                    break
                for nick in nickNameList:
                    if len(re.findall(address, nick)) > 0:
                        addressFlag = True
                        break
            if addressFlag: break
        if not addressFlag:
            return False
        ## 判断是否还有屏蔽词，有即去掉
        keyScapes = self.keysScapes.split(" ")
        for keyTag in keyTags:
            for keyScape in keyScapes:
                if len(re.findall(keyScape,keyTag)) > 0:
                    return False

        ## 判断是否还有污染类关键词语
        keys = self.keysList.split(" ")
        keys.append("治理")
        keys.append("保护")
        for keyTag in keyTags:
            for key in keys:
                if len(re.findall(key,keyTag)) > 0:
                    return True
        return False

    # def wbAnalyze(self,comment):
    #     pattern = '[\u4e00-\u9fff]+'
    #     re_compile = re.compile(pattern)
    #     chList = re_compile.findall(comment)
    #     if len(chList) == 0:
    #         return False
    #     chRes = "".join(chList)
    #     return self.wbKeyAnalyze(chRes)
    def wbKeyAnalyze(self,chText):
        addressFlag = False
        ## 判断位置是否正确
        for address in self.addresses:
            if len(re.findall("第.个" + address, chText)) > 0:
                return False
            if len(re.findall(address,chText)) > 0:
                addressFlag = True
                break
        if not addressFlag:
            return False
        ## 判断是否还有屏蔽词，有即去掉
        keyScapes = self.keysScapes.split(" ")
        for keyScape in keyScapes:
            if len(re.findall(keyScape, chText)) > 0:
                    return False

        ## 判断是否还有污染类或者保护类关键词语
        keys = self.keysList.split(" ")
        keys.append("治理")
        keys.append("保护")
        for key in keys:
            if len(re.findall(key, chText)) > 0:
                return True
        return False





