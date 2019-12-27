import urllib.request as urlRequest
import urllib.parse as urlParse
from bs4 import BeautifulSoup

import configparser
import os
import time
import datetime
import re
import traceback
from threading import Thread as thread
import threading
class weather(thread):
    def __init__(self, file,conn):
        thread.__init__(self)
        self.configFile = os.getcwd() + file
        self.conn = conn
        self.stations = dict()
        self.initStation()
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

    def initWeatherAttr(self, conf, weatherConfAttr):
        self.attrKeyDictDayOne = dict()
        self.attrKeyDictDayThree = dict()
        self.attrKeyDictDaySix = dict()
        ttime = conf.get(weatherConfAttr[1], "ttime")
        t = conf.get(weatherConfAttr[1], "t")
        po = conf.get(weatherConfAttr[1], "po")
        u = conf.get(weatherConfAttr[1], "u")
        dd = conf.get(weatherConfAttr[1], "dd")
        ff = conf.get(weatherConfAttr[1], "ff")

        self.dbNameDict = {ttime: "ttime",t: "t",
                              po: "po", u: "u",
                              dd: "dd", ff: "ff"}
        ## 历史配置内容
        self.historyCity = conf.get(weatherConfAttr[2],"historyCity")
        self.historyUrl = conf.get(weatherConfAttr[2],"url") + urlParse.quote(self.historyCity)
        self.tableId = conf.get(weatherConfAttr[2],"tableId")
        self.titleContentDiv=conf.get(weatherConfAttr[2],"titleContentClass")
        self.hisNameDict = dict()
        for name1,name2 in zip(conf.get(weatherConfAttr[2],"dbName").split(","),conf.get(weatherConfAttr[2],"titleName").split(",")):
            self.hisNameDict[name2] = name1
        self.hisNameDict["TT"] = "ttime"

    def weatherSpider(self,station,requestUrl):
        request = urlRequest.Request(requestUrl)
        response = urlRequest.urlopen(request)
        if not response:
            self.conn.saveLogInfo("weather", "%s天气预报数据为空"%station,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        soup = BeautifulSoup(response, 'lxml')
        ## 爬取一天预报
        self.spiderForFc(soup, self.fcTableOne,1,station)

        ## 爬取三天预报
        self.spiderForFc(soup,self.fcTableThree,3,station)

        ## 爬取六天预报
        self.spiderForFc(soup,self.fcTableSix,6,station)

    def spiderForFc(self, soup, tableId,type,station):
        tableContent = soup.find("table", {"id": tableId})
        if tableContent == None:
            self.conn.saveLogInfo("weather", "%s天气预报数据为空" % station,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            return
        ## 获取所有降雨量
        rrrList = tableContent.findAll("div",{"class":self.rrrClass})
        if rrrList == None:
            self.conn.saveLogInfo("weather", "%s天气预报数据中降雨量数据为空" % station,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            return
        trList = tableContent.findAll('tr')

        ## 获取不同日期的时刻数目
        firstLine = trList[0].findAll('td')
        firstLine.pop(0)
        dayPosition = 0

        resultDict = list()

        timeSumLength = 0

        for td in firstLine:
            dayDict = dict()
            tempDate = (datetime.datetime.now()+datetime.timedelta(days=dayPosition)).strftime("%Y-%m-%d")
            dayDict["time"] = tempDate
            length = td["colspan"]
            timeSumLength += int(length) // 2
            dayDict["len"] = int(length) // 2
            dayDict["data"] = list()
            resultDict.append(dayDict)
            dayPosition += 1
        trList.pop(0)

        dayLength = 0
        ## 解析所有rrr雨量数据
        preLength = 0
        for k in range(timeSumLength):
            if "onmouseover" in rrrList[2 * k].attrs:
                rrr1 = rrrList[2 * k].attrs["onmouseover"]
            else:
                rrr1 = ""
            if "onmouseover" in rrrList[2 * k + 1].attrs:
                rrr2 = rrrList[2 * k].attrs["onmouseover"]
            else:
                rrr2 = ""
            rr1Number = re.findall(",.*\\((.*)毫米",rrr1)
            rr2Number = re.findall(",.*\\((.*)毫米",rrr2)
            count = 0
            if not len(rr1Number):
                rr1Number = 0
            else:
                count += 1
                rr1Number = float(rr1Number[0])
            if not len(rr2Number):
                rr2Number = 0
            else:
                count += 1
                rr2Number = float(rr2Number[0])
            temp = dict()
            if count > 0:
                temp["rrr"] = (rr1Number + rr2Number) / count
            else:
                temp["rrr"] = 0
            if k - preLength < resultDict[dayLength]["len"]:
                resultDict[dayLength]["data"].append(temp)
            else:
                preLength += resultDict[dayLength]["len"]
                dayLength += 1
                resultDict[dayLength]["data"].append(temp)

        ## 将需要的信息解析到dict中
        for tr in trList:
            tdList = tr.findAll("td")
            firstName = tdList.pop(0).text
            key = self.keyInDict(firstName)
            if key:
                timeLength = 0
                dayLength = 0
                for td in tdList:
                    res = td.text.strip()
                    if self.dbNameDict[key] == "t":
                        if len(res.split(" ")[0]) > 0:
                            res = res.split(" ")[0].replace("+","")
                        else:
                            res = ""
                    if self.dbNameDict[key] == "po":
                        divList = td.findAll("div")
                        res = None
                        for div in divList:
                            if "style" not in div.attrs:
                                res = div.text
                                break
                        if res is None:
                            res = ""
                    if self.dbNameDict[key] == "ff":
                        if len(res.split(" ")[0]) > 0:
                            res =res.split(" ")[0]
                        else:
                            res = ""
                    if timeLength < resultDict[dayLength]["len"]:
                        resultDict[dayLength]["data"][timeLength][self.dbNameDict[key]] = res
                    else:
                        timeLength = 0
                        dayLength += 1
                        resultDict[dayLength]["data"][timeLength][self.dbNameDict[key]] = res
                    timeLength += 1

        ## 保存数据库中
        self.conn.saveWeatherData(resultDict,station,type)
    # 判断key是否存在字典中
    def keyInDict(self,name):
        for key in self.dbNameDict:
            if name.find(key) >= 0:
                return key
        return None
    # 时间差返回的是秒数
    def timeDelta(self):

        ## 获取数据库当前时间信息
        ##
        dbTime = "2017.01.17 13:00"
        nowTime = datetime.datetime.now()
        db = datetime.datetime.strptime(dbTime, "%Y.%m.%d %H:%M")
        timeDelta = nowTime - db
        timeDelta.total_seconds()
        return timeDelta.total_seconds()

    def initStation(self):
        dbStatement = "SELECT stationname,prediction FROM media.station"
        rows = self.conn.sqlExec(dbStatement,type=1)
        for row in rows:
            self.stations[row[0]] = row[1]

    def spiderHistoryData(self):
        req = urlRequest.Request(self.historyUrl)
        res = urlRequest.urlopen(req)
        if not res:
            self.conn.saveLogInfo("weather", "天气历史数据为空",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "天气历史数据为空  " + "运行状态: " + str(1))
        soup = BeautifulSoup(res,"lxml")
        tableContent = soup.find("table",{"id":self.tableId})
        trList = tableContent.findAll("tr")
        if len(trList) == 0:
            self.conn.saveLogInfo("weather", "天气历史数据为空",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "天气历史数据为空  " + "运行状态: " + str(1))
        titileContent = trList.pop(0)
        titleDivList = titileContent.findAll("div",{"class":self.titleContentDiv})
        titleNamePositon = dict()
        position = 0
        for div in titleDivList:
            if div.text in self.hisNameDict:
                titleNamePositon[position] = div.text
                position += 1
                continue
            position += 1
        titleNamePositon[0] = "TT"
        dayHour = dict()
        for tr in trList:
            for td in tr.findAll("td"):
                if "rowspan" in td.attrs:
                    dayHour[int(td["rowspan"])] = self.hisFormatTime(td.text)
                    td.decompose()
        preDayHour = 0
        for day in dayHour:
            date = dayHour[day]
            for hour in range(day):
                position = 0
                resultDict = dict()
                for td in trList[hour + preDayHour].findAll("td"):
                    if position in titleNamePositon:
                        dbDictName = self.hisNameDict[titleNamePositon[position]]
                        valueStr = td.text.strip()
                        if dbDictName == "t":
                            valueStr = valueStr.split(" ")[0]
                        if dbDictName == "po":
                            valueStr = valueStr.split(" ")[2]
                        if dbDictName == "ff":
                            splitStr = valueStr.split(" ")
                            if len(splitStr) <= 1 :
                                valueStr = splitStr[0]
                            else:
                                valueStr = splitStr[0]+ splitStr[1] + splitStr[2]
                        if dbDictName == "td":
                            valueStr = valueStr.split(" ")[0]
                        if dbDictName == "ttime":
                            valueStr = date + " " + valueStr + ":00"
                        resultDict[dbDictName] = valueStr
                        position += 1
                        continue
                    position += 1
                resultDict["station"] = re.findall("(.*)历史天气_",self.historyCity)[0]
                self.conn.saveHistoryData(resultDict,"media.webweatherreal")
            preDayHour += day
        self.conn.saveLogInfo("weather", "天气历史数据抓取完毕", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "天气历史数据抓取完毕  " + "运行状态: " + str(1))
    def hisFormatTime(self,str):
        str=str.strip()
        str = re.findall("(.*)星期",str)[0]
        str = str.replace(" ","")
        str = str.replace("年",".")
        str = str.replace("月",".")
        str = str.replace("日","")
        timeArray = time.strptime(str, "%Y.%m.%d")
        newStyleTime = time.strftime("%Y.%m.%d", timeArray)
        return newStyleTime


    def loadConf(self):
        self.conn.saveLogInfo("weather", "读取天气配置文件", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "读取天气配置文件  " + "运行状态: " + str(1))
        conf = configparser.ConfigParser()
        conf.read(self.configFile, encoding="utf-8")
        self.fcTableOne = conf.get(conf.sections()[0], "fcTableOne")
        self.fcTableThree = conf.get(conf.sections()[0], "fcTableThree")
        self.fcTableSix = conf.get(conf.sections()[0], "fcTableSix")
        self.rrrClass = conf.get(conf.sections()[0],"rrClass")
        self.initWeatherAttr(conf,conf.sections())
    ## 每个小时抓取一次
    def run(self):
        self.conn.saveLogInfo("weather", "天气线程开始运行", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "天气线程开始运行  " + "运行状态: " + str(1))
        try:
            while self.__running.isSet():
                self.__flag.wait()
                for key in self.stations:
                    self.conn.saveLogInfo("weather", "抓取%s城市预报数据" % key,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "抓取%s城市预报数据  " % key + "运行状态: " + str(1))
                    self.weatherSpider(key, self.stations[key])
                self.conn.saveLogInfo("weather", "爬取天气预报数据结束",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "爬取天气预报数据结束  " + "运行状态: " + str(1))
                ## 抓取历史数据
                self.conn.saveLogInfo("weather", "爬取天气历史数据",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "爬取天气历史数据   " + "运行状态: " + str(1))
                self.spiderHistoryData()
                self.conn.saveLogInfo("weather", "爬取天气历史数据结束", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "爬取天气历史数据结束   " + "运行状态: " + str(1))
                time.sleep(2500)
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
            exString = exString.replace("'","")
            self.conn.saveLogInfo("weather", "天气线程异常%s"%exString, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "爬取天气历史数据结束   " + "运行状态: " + str(0))
        else:
            self.conn.saveLogInfo("weather", "天气线程异常,异常内容为空",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "天气线程异常,异常内容为空   " + "运行状态: " + str(0))
    def dbReset(self,db):
        self.conn = db
