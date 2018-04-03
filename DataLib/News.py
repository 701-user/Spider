import urllib.request as urlRequest
import urllib.parse as urlParse
from bs4 import BeautifulSoup

import configparser
import os
import re
import datetime
import time
import traceback

from threading import Thread as thread
import threading
class new(thread):
    def __init__(self,file,conn):
        thread.__init__(self)
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

        self.configFile = os.getcwd() + file
        self.conn = conn
        self.exception=None

    def pause(self):
        self.__flag.clear()
    def resume(self):
        self.__flag.set()
    def stop(self):
        self.__flag.set()
        self.__running.clear()

    def spiderNews(self,keys):
        self.conn.saveLogInfo("news", "正在抓取新闻信息.....", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "正在抓取新闻信息.....  " + "运行状态: " + str(1))

        for key in keys:
            self.spider(key)

    def spider(self,key):
        # startTime = datetime
        req = urlRequest.Request(self.newsUrl + urlParse.quote(key))
        res = urlRequest.urlopen(req)
        soup = BeautifulSoup(res,"lxml")
        divContent = soup.find("div",{"class":self.divClass})
        if not divContent:
            self.conn.saveLogInfo("news", "抓取的新闻数据为空", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "抓取的新闻数据为空.....  " + "运行状态: " + str(1))
            return
        ulContent = divContent.find("ul")
        for li in ulContent.findAll("li"):
            result = dict()
            a = li.find("a")
            result["caption"] =a.text
            span = li.find("span")
            result["dtime"] = re.findall("\[(.*)\]",span.text)[0]
            result["class"] = "ynshbt"
            result["href"] = a["href"]
            self.conn.saveNews(result,"media.news")

    def judgeTime(self,spiderTime,dbTime):
        spiderResult = ""
        for ch in spiderTime:
            if ch == '(' or ch == ')':
                continue
            spiderResult += ch
        spider = datetime.datetime.strptime(spiderResult, "%Y-%m-%d")
        db = datetime.datetime.strptime(dbTime, "%Y-%m-%d")
        return spider > db,spiderResult

    def loadConf(self):
        self.conn.saveLogInfo("news", "读取新闻配置文件", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "读取新闻配置文件  " + "运行状态: " + str(1))
        conf = configparser.ConfigParser()
        conf.read(self.configFile,encoding="utf-8")
        newsSection = conf.sections()
        self.newsUrl = conf.get(newsSection[0],"url")
        self.divClass = conf.get(newsSection[0],"div")

    ## 新闻每天晚上12点抓取一次
    def run(self):
        self.conn.saveLogInfo("news", "新闻线程开始运行", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "新闻线程开始运行  " + "运行状态: " + str(1))
        try:
            keys = self.conn.getNewsWebKey()
            while self.__running.isSet():
                self.__flag.wait()
                hour = datetime.datetime.now().hour
                if hour == 11:
                    self.conn.saveLogInfo("news", "新闻信息开始抓取", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " news " + "新闻信息开始抓取  " + "运行状态: " + str(1))
                    self.spiderNews(keys)
                    self.conn.saveLogInfo("news", "新闻信息抓取完毕", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " news " + "新闻信息抓取完毕  " + "运行状态: " + str(1))
                time.sleep(3600)
        except Exception as e:
            self.exTrace = traceback.format_exc()
            self.exception = e
            traceback.print_exc()
    def getException(self):
        if self.exception:
            exString = ""
            for arg in self.exception.args:
                exString += str(arg)
            if not self.exTrace:
                exString += self.exTrace
            exString = exString.replace("'", "")
            self.conn.saveLogInfo("news", "新闻线程异常,异常内容为%s"%exString, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "新闻线程异常,异常内容为%s   "%exString + "运行状态: " + str(0))
        else:
            self.conn.saveLogInfo("news","新闻线程异常,未找到异常", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "新闻线程异常,未找到异常  " + "运行状态: " + str(0))

    def dbReset(self,db):
        self.conn = db
    # def getName(self):
    #     print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"新闻")