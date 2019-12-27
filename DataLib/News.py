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

    def spiderNews(self,dbLastTime):
        self.conn.saveLogInfo("news", "正在抓取新闻信息.....", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "正在抓取新闻信息.....  " + "运行状态: " + str(1))
        self.spider(dbLastTime)

    def spider(self,dbLastTime):
        index_news_url = self.newsUrl
        while True:
            req = urlRequest.Request(index_news_url)
            res = urlRequest.urlopen(req)
            soup = BeautifulSoup(res,"lxml")
            divContent = soup.find("div",{"class":self.divContent})
            divListPage = soup.find("div",{"class": self.divPageList})
            if not divContent:
                self.conn.saveLogInfo("news", "抓取的新闻数据为空", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "抓取的新闻数据为空.....  " + "运行状态: " + str(1))
                return
            ulContentList = divContent.findAll("ul")
            a_page_list = divListPage.findAll("a")
            next_page_url = None
            for aContent in a_page_list:
                if aContent.text == "下一页":
                    next_page_url = aContent["href"]
                    break
            if next_page_url == None:
                return
            index_news_url = next_page_url
            for ulContent in ulContentList:
                for li in ulContent.findAll("li"):
                    result = dict()
                    a = li.find("a")
                    result["caption"] =a.text
                    span = li.find("span")
                    news_time = re.findall("\((.*?)\)",span.text)[0]
                    if self.judgeTime(news_time,dbLastTime):
                        result["dtime"] = news_time
                        result["class"] = "ynshbt"
                        result["href"] = a["href"]
                        self.conn.saveNews(result,"media.news")
                    else:
                        return

    def judgeTime(self, spiderTime, dbTime):
        spider = datetime.datetime.strptime(spiderTime, "%Y-%m-%d")
        db = datetime.datetime.strptime(dbTime, "%Y-%m-%d")
        return spider > db

    def loadConf(self):
        self.conn.saveLogInfo("news", "读取新闻配置文件", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "读取新闻配置文件  " + "运行状态: " + str(1))
        conf = configparser.ConfigParser()
        conf.read(self.configFile,encoding="utf-8")
        newsSection = conf.sections()
        self.newsUrl = conf.get(newsSection[0],"url")
        self.divContent = conf.get(newsSection[0],"div_content")
        self.divPageList = conf.get(newsSection[0], "div_page_list")

    ## 新闻每天下午11点抓取一次
    def run(self):
        self.conn.saveLogInfo("news", "新闻线程开始运行", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "新闻线程开始运行  " + "运行状态: " + str(1))
        try:
            while self.__running.isSet():
                self.__flag.wait()
                hour = datetime.datetime.now().hour
                if hour == 23:
                    self.conn.saveLogInfo("news", "新闻信息开始抓取", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    dbLatestTime = self.conn.newsLastestTime()
                    dbLatestTime = dbLatestTime[0].strftime("%Y-%m-%d")
                    print(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " news " + "新闻信息开始抓取  " + "运行状态: " + str(1))
                    self.spiderNews(dbLatestTime)
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
#
# """
# 单元测试
# """
# def test():
#     nn = new("\\config\\news.ini",None)
#     nn.loadConf()
#     nn.start()
# test()