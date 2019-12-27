import urllib.request as urlRequest
from bs4 import BeautifulSoup
import configparser
import os
import re
import datetime
import time
import traceback
from threading import Thread as thread
import threading
class water(thread):
    def __init__(self,file,conn):
        thread.__init__(self)
        self.configFile = os.getcwd() + file
        self.conn = conn
        self.waterRank = {'——':0,'--':0,
            'Ⅰ':1,'Ⅱ':'2','Ⅲ':'3','Ⅳ':'4',
            'Ⅴ':'5','>Ⅰ':10,'>Ⅱ':20,'>Ⅲ':30,
            '>Ⅳ':40,'>Ⅴ':50}
        self.exception = None
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()
    def pause(self):
        self.__flag.clear()
    def resume(self):
        self.__flag.set()
    def stop(self):
        self.__flag.set()
        self.__running.clear()

    def loadErhaiAttri(self,conf,waterSection):
        self.erHaiDict = dict()
        self.erHaiDict[int(conf.get(waterSection[2], "affiliation"))] = "affiliation"
        self.erHaiDict[int(conf.get(waterSection[2], "part"))] = "part"
        self.erHaiDict[int(conf.get(waterSection[2], "waterclass"))] = "waterclass"
        self.erHaiDict[int(conf.get(waterSection[2], "define"))] = "define"
        self.erHaiDict[int(conf.get(waterSection[2], "excpara"))] = "excpara"
        self.erHaiDict[int(conf.get(waterSection[2], "transp"))] = "transp"
        self.erHaiDict[int(conf.get(waterSection[2], "note"))] = "note"
        self.erHaiwaterClass = int(conf.get(waterSection[2], "waterclass"))
    def loadOtherRiverAttri(self,conf,waterSection):
        self.otherRiverDict = dict()

        self.otherRiverDict[int(conf.get(waterSection[3], "river"))] = "river"
        self.otherRiverDict[int(conf.get(waterSection[3], "monitorname"))] = "monitorname"
        self.otherRiverDict[int(conf.get(waterSection[3], "affiliation"))] = "affiliation"
        self.otherRiverDict[int(conf.get(waterSection[3], "waterclass"))] = "waterclass"
        self.otherRiverDict[int(conf.get(waterSection[3], "excpara"))] = "excpara"
        self.otherRiverDict[int(conf.get(waterSection[3], "note"))] = "note"
        self.otherRiverDict[0] = "dtime"
        self.otherRiverDict[1] = "index"
        self.waterClass = int(conf.get(waterSection[3], "waterclass"))


    ## 该方法主要用于初始化的时候将数据库中最新的和运行之间
    ## 缺少的水质数据添加到数据库中
    ## 只在程序初始运行时候执行
    def spiderInitWaterData(self):
        dbLatestTime = self.conn.waterLatestTime()
        if not dbLatestTime:
            self.conn.saveLogInfo("water", "水质数据库为空,抓取为期1年的水质数据",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " water " + "水质数据库为空,抓取为期1年的水质数据  " + "运行状态: " + str(1))
            dbLatestTime=datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            dbLatestTime=dbLatestTime[0].strftime("%Y-%m-%d")
        if not self.spider(self.waterIndexUrl,dbLatestTime):
            ## 后续页数
            ## 获取所有页数url
            request = urlRequest.Request(self.waterIndexUrl)
            reponse = urlRequest.urlopen(request)
            soup = BeautifulSoup(reponse, "lxml")

            pageIdList = soup.findAll("div",{"class":self.pageClass})
            pageUrlList = list()
            aList = pageIdList.findAll("a").pop(0)
            for a in aList:
                pageUrlList.append(a["href"])
            for pageUrl in pageUrlList:
                if not self.spider(pageUrl,dbLatestTime):
                    continue
                else:
                    break

    def spider(self,indexUrl,dbTime):
        request = urlRequest.Request(indexUrl)
        reponse = urlRequest.urlopen(request)

        soup = BeautifulSoup(reponse, "lxml")

        for ul in soup.findAll("ul", {"class": self.indexUl}):
            for li in ul.findAll("li"):
                recordTime = re.findall("\((.*)\)", li.find("a").text)[0]
                recordTime = recordTime.replace("年", "-")
                recordTime = recordTime.replace("月", "-") + "01"
                if self.judgeTime(recordTime, dbTime):
                    reportUrl = li.find("a")["href"]
                    ## 请求report数据并爬取相关数据
                    self.reportSpider(reportUrl,recordTime)
                else:
                    return True
        return False
    ## 水质报告爬虫
    def reportSpider(self,url,recordTime):

        request = urlRequest.Request(url)
        reponse = urlRequest.urlopen(request)

        soup = BeautifulSoup(reponse, "lxml")
        divContent = soup.find("div", {"class": self.divClass})

        tableList = divContent.findAll("table")

        ##处理洱海表格数据
        erHaiTable = tableList[0]
        trList = erHaiTable.findAll("tr")
        trList.pop(0)
        trList.pop(len(trList)-1)

        resultList = list()
        rowResult = dict()
        tdPosition = 1
        for td in trList[0].findAll("td"):
            value = td.text.replace("\r\n", "")
            value = value.replace(" ", "")
            if value in self.waterRank:
                rowResult[self.erHaiDict[tdPosition]] = self.waterRank[value]
                tdPosition += 1
                continue
            rowResult[self.erHaiDict[tdPosition]] = value
            tdPosition += 1
        trList.pop(0)
        rowResult["dtime"] = recordTime
        resultList.append(rowResult)
        for tr in trList:
            tdPosition = 1
            newRowResult = dict()
            newRowResult[self.erHaiDict[tdPosition]] = rowResult[self.erHaiDict[tdPosition]]
            tdPosition += 1
            for td in tr.findAll("td"):
                value = td.text.replace("\r\n", "")
                value = value.replace(" ", "")
                if value in self.waterRank and tdPosition == self.erHaiwaterClass:
                    newRowResult[self.erHaiDict[tdPosition]] = self.waterRank[value]
                    tdPosition += 1
                    continue
                newRowResult[self.erHaiDict[tdPosition]] = value
                tdPosition += 1
            newRowResult[self.erHaiDict[tdPosition]] = rowResult[self.erHaiDict[tdPosition]]
            tdPosition += 1
            newRowResult[self.erHaiDict[tdPosition]] = rowResult[self.erHaiDict[tdPosition]]
            newRowResult["dtime"] = recordTime
            resultList.append(newRowResult)
        ## 保存数据到数据库中
        self.conn.saveWater(resultList,"media.erhaireport")

        ## 处理其他河流数据
        otherRiver = tableList[1]
        trList = otherRiver.findAll("tr")
        trList.pop(0)
        trList.pop(len(trList) - 1)
        ## FIXME THE DIFFERENT TABLE HOW TO EBABDED THEM
        all_tr_info = list()
        for i in range(len(trList)):
            trDict = dict()
            trDict[self.otherRiverDict[0]] = recordTime
            trDict[self.otherRiverDict[1]] = None
            trDict[self.otherRiverDict[2]] = None
            trDict[self.otherRiverDict[3]] = None
            trDict[self.otherRiverDict[4]] = None
            trDict[self.otherRiverDict[5]] = None
            trDict[self.otherRiverDict[6]] = None
            trDict[self.otherRiverDict[7]] = None
            all_tr_info.append(trDict)
        for i,tr in enumerate(trList):
            tdList = tr.findAll("td")
            tdPosition = 1
            for td in tdList:
                rowLen = 1
                if "rowspan" in td.attrs:
                    rowLen = int(td["rowspan"])
                value = td.text.replace("\r\n", "")
                value = value.replace(" ", "")
                if value in self.waterRank:
                    value = self.waterRank[value]
                if rowLen == 1:
                    for tdValue in all_tr_info[i]:
                        if all_tr_info[i][tdValue] is None:
                            all_tr_info[i][tdValue] = value
                            break
                else:
                    for k in range(rowLen):
                        all_tr_info[i + k][self.otherRiverDict[tdPosition]] = value
                tdPosition += 1
        ## 保存数据到数据库中
        for info in all_tr_info:
            info.pop("index")
        self.conn.saveWater(all_tr_info, "media.waterreport")
    def judgeTime(self,spiderTime,dbTime):
        spider = datetime.datetime.strptime(spiderTime, "%Y-%m-%d")
        db = datetime.datetime.strptime(dbTime, "%Y-%m-%d")
        return spider > db

    def loadConf(self):
        self.conn.saveLogInfo("water", "读取水质配置文件", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " water " + "读取水质配置文件  " + "运行状态: " + str(1))
        conf = configparser.ConfigParser()
        conf.read(self.configFile, encoding="utf-8")
        waterSection = conf.sections()
        self.waterIndexUrl = conf.get(waterSection[0], "indexUrl")
        self.indexUl = conf.get(waterSection[1], "indexUl")
        self.pageClass = conf.get(waterSection[1], "indexPage")

        self.divClass = conf.get(waterSection[2], "div")

        self.loadErhaiAttri(conf, waterSection)
        self.loadOtherRiverAttri(conf, waterSection)
        try:
            self.spiderInitWaterData()
        except Exception as e:
            self.exception = e
            self.conn.saveLogInfo("water", "水质线程初始化异常，%s" % str(e), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " water " + "水质线程初始化异常，%s   " % str(e) + "运行状态: " + str(1))
    ## 初始化之后抓取数据
    ## 每周周一至周五,每天抓取一次水质数据
    def run(self):
        self.conn.saveLogInfo("water", "水质线程运行", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " water " + "水质线程运行  " + "运行状态: " + str(1))
        try:
            while self.__running.isSet():
                self.__flag.wait()
                weekday = datetime.datetime.now().weekday()
                if 5 >= weekday >= 1:
                    dbLatestTime = self.conn.waterLatestTime()
                    dbLatestTime=dbLatestTime[0].strftime("%Y-%m-%d")
                    self.conn.saveLogInfo("water", "正在抓取水质信息.....",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " water " + "正在抓取水质信息.....  " + "运行状态: " + str(1))
                    self.spider(self.waterIndexUrl, dbLatestTime)
                    self.conn.saveLogInfo("water", "水质信息抓取完毕",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " water " + "水质信息抓取完毕  " + "运行状态: " + str(1))
                time.sleep(86400)
        except Exception as e:
            traceback.print_exc()
            self.exTrace = traceback.format_exc()
            self.exception = e
    def getException(self):
        if self.exception:
            exString = ""
            for arg in self.exception.args:
                exString += str(arg)
            if not self.exTrace:
                exString += self.exTrace
            exString = exString.replace("'", "")
            self.conn.saveLogInfo("water", "水质线程异常:%s"%exString, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " water " + "水质线程异常:%s  "%exString + "运行状态: " + str(0))
        else:
            self.conn.saveLogInfo("water", "水质线程异常，未找到异常",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " water " + "水质线程异常，未找到异常  " + "运行状态: " + str(0))

    def dbReset(self,db):
        self.conn = db