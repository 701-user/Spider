import configparser
import os
import json
import urllib.request as urlRequest
from bs4 import BeautifulSoup
import time
import datetime
import traceback
from threading import Thread as thread
import threading
class aqi(thread):
    def __init__(self,file,conn):
        thread.__init__(self)
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

        self.configFile = os.getcwd() + file
        self.conn = conn
        self.exception = None

    def pause(self):
        self.__flag.clear()
    def resume(self):
        self.__flag.set()
    def stop(self):
        self.__flag.set()
        self.__running.clear()
    def spider(self):
        self.conn.saveLogInfo("aqi", "正在抓取AQI空气信息....",
                                  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " aqi " + "正在抓取AQI空气信息...  " + "运行状态: " + str(1))
        url = self.url + self.token
        req = urlRequest.Request(url)
        res = urlRequest.urlopen(req)
        if res != None:
            soup = BeautifulSoup(res,"lxml")
            aqiDetailJson = json.loads(soup.text)
            ## 使用json 文件测试
            # jsonFile = os.getcwd()+"/json/ariQuality.json"
            # fp = open(jsonFile,encoding="utf-8")
            # aqiDetailJson = json.load(fp)
            if "error" in aqiDetailJson:
                self.conn.saveLogInfo("aqi", aqiDetailJson["error"], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " aqi " + aqiDetailJson["error"] +"  " + "运行状态: " + str(1))
                return -1
            for aqi in aqiDetailJson:
                if aqi["position_name"] == None:
                    aqiDetailJson.remove(aqi)
            self.conn.saveAqiData(aqiDetailJson,self.dbNameList)



        # tabelContent = soup.find("table", {"id": self.tabelId})
        # timeClass = soup.find("div",{"class":"live_data_time"})
        # time = re.findall("时间：(.*)",timeClass.find("p").text)[0]
        # tb = tabelContent.find("tbody")


        # if tb:
        #     for tr in tb.findAll("tr"):
        #
        #         order = 1
        #         resultDict = dict()
        #         for td in tr.findAll("td"):
        #             if "class" in td.attrs:
        #                 continue
        #             resultDict[self.tdOrder[order]] = td.text
        #             order += 1
        #         resultDict["timepoint"]=time
        #         resultDict["co_24h"]= '0.7'
        #         resultDict['no_24h'] = "0.591"
        #         resultDict['o3_24h'] = ''
        #         resultDict['o3_24h'] =47
        #         resultDict['pm10_24h'] = 35
        #         resultDict['pm25_24h'] = 28
        #         ## TODO 插入数据库
        #         print("插入数据库")
        #         sqlStatment = "INSERT INTO media.airquality ('positionname','timepoint','co','co_24h','no','no_24h'," \
        #                       "'o3','o3_24h','pm10','pm10_24h','pm25','pm25_24h','so2','so2_24h','primarypollutant','quality')" \
        #                       "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" \
        #                       %(resultDict['positionname'],resultDict['timepoint'],resultDict['co'],resultDict['co_24h'],resultDict['no'],
        #                         resultDict['no_24h'],resultDict['o3'],resultDict['o3_24h'],resultDict['pm10'],resultDict['pm10_24h'],resultDict['pm25'],
        #                         resultDict['pm25_24h'],resultDict['so2'],resultDict['so2_24h'],resultDict['primarypollutant'],resultDict['quality'])
        #         self.conn.sqlExec(sqlStatment,type=1)

    def loadConf(self):
        self.conn.saveLogInfo("aqi", "读取AQI配置文件", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " aqi " + "读取AQI配置文件  " + "运行状态: " + str(1))
        conf = configparser.ConfigParser()
        conf.read(self.configFile,"utf-8")
        self.url = conf.get(conf.sections()[0],"url")

        self.dbNameList = conf.get(conf.sections()[1],"dbDict").split(",")

        self.token = conf.get(conf.sections()[1],"token")
    ## Aqi数据每半小时抓取一次
    def run(self):
        self.conn.saveLogInfo("aqi", "AQI线程开始运行",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " aqi " + "AQI线程开始运行  " + "运行状态: " + str(1))
        try:
            while self.__running.isSet():
                self.__flag.wait()
                self.conn.saveLogInfo("aqi", "AQI信息开始抓取", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " aqi " + "AQI信息开始抓取  " + "运行状态: " + str(1))
                self.spider()
                self.conn.saveLogInfo("aqi", "AQI信息抓取完毕", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " aqi " + "AQI信息抓取完毕  " + "运行状态: " + str(1))
                time.sleep(2700)
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
            self.conn.saveLogInfo("aqi", "AQI线程异常,异常内容为%s"%exString, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " aqi " + "AQI线程异常,异常内容为%s  "%exString + "运行状态: " + str(0))
        else:
            self.conn.saveLogInfo("aqi", "aqi线程异常内容为空", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
            print(datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S") + " aqi " + "AQI线程异常,异常内容为空  " + "运行状态: " + str(0))
    def dbReset(self,db):
        self.conn = db