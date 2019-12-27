import configparser
import traceback
import psycopg2
import datetime
import time
from selenium import webdriver
from DataLib.Encoder import encoder
import os
import uuid
import shutil
## 使用的是postgresql数据库
class dataBase:
    INSERT,SELECT = 0,1
    def __init__(self,configFile):
        self.dbConn = None
        self.confFile = os.getcwd() + configFile

    def loadConfig(self):
        print("读取数据库配置文件")
        conf = configparser.ConfigParser()
        ## TODO 解密方式待定
        ## 从 C:/windows/system32/文件夹下
        conf.read(self.confFile,'utf-8')

        #本地数据库测试
        # self.userName = conf.get(conf.sections()[4], "12KdT")
        # self.password = conf.get(conf.sections()[4], "ASdc")
        # self.host = conf.get(conf.sections()[4], "Qwest")
        # self.port = conf.get(conf.sections()[4], "Pk1533")
        # self.databaseName =conf.get(conf.sections()[4], "ddO")

        # 数据库字段解密
        # t = conf.sections()
        self.userName = conf.get(conf.sections()[0], "12KdT")
        self.password = conf.get(conf.sections()[0], "ASdc")
        self.host = conf.get(conf.sections()[0], "Qwest")
        self.port = conf.get(conf.sections()[0], "Pk1533")
        self.databaseName =conf.get(conf.sections()[0], "ddO")

        # 解密过程
        pc = encoder()  # 初始化密钥
        self.userName = pc.decrypt(self.userName)
        self.password = pc.decrypt(self.password)
        self.host = pc.decrypt(self.host)
        self.port = pc.decrypt(self.port)
        self.databaseName = pc.decrypt(self.databaseName)

        while self.connectDB() != True:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 数据库连接失败，请检查相关配置")
            time.sleep(1200)
            self.userName = conf.get(conf.sections()[0], "12KdT")
            self.password = conf.get(conf.sections()[0], "ASdc")
            self.host = conf.get(conf.sections()[0], "Qwest")
            self.port = conf.get(conf.sections()[0], "Pk1533")
            self.databaseName = conf.get(conf.sections()[0], "ddO")
            ## 解密过程
            pc = encoder()  # 初始化密钥
            self.userName = pc.decrypt(self.userName)
            self.password = pc.decrypt(self.password)
            self.host = pc.decrypt(self.host)
            self.port = pc.decrypt(self.port)
            self.databaseName = pc.decrypt(self.databaseName)
    # 数据库连接操作
    def connectDB(self):
        ##TODO 连接数据库
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"连接数据库")
        try:
            self.dbConn = psycopg2.connect(database = self.databaseName,
                                           user = self.userName,
                                           password = self.password,
                                           host = self.host,
                                           port = self.port)
        except Exception as e:
            traceback.print_exc()
            return False
        ## TODO 添加数据库连接是否成功操作
        if self.dbConn :
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"连接数据库成功")
            self.saveLogInfo("main", "数据库初始化结束", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            # sqlStament = "select * from media.address"
            # result = self.sqlExec(sqlStament,type = 1)
            # for row in result:
            #     print("address is " + row[0] + "longitude is "+ str(row[1])+
            #           "latitude is " + str(row[2]) + "affilication is " + row[3])
            return True
        else:
            return False

    def testConnecting(self):
        sql = "select * from media.station"
        result = self.sqlExec(sql,self.SELECT)
        if len(result) < 0:
            return False
        return True
    ##------------------------------------------------------
    ## sql语句分析部分
    ##------------------------------------------------------
    def sqlExec(self,sqlStatement,type):
        cur = self.dbConn.cursor()
        cur.execute(sqlStatement)
        self.dbConn.commit()
        ## type 为 0 表示insert语句,返回影响的行数
        if type == self.INSERT:
            return cur.rowcount
        ## type 为1 表示为select语句，返回查询结果
        if type == self.SELECT:
            return cur.fetchall()

    ##-----------------------------------------------------
    ##存储log信息
    ##-----------------------------------------------------
    def saveLogInfo(self,category,info,ttime,status):
        sqlStatement = "INSERT INTO media.log (category,info,status,ttime) VALUES ('"+ category + "','"+ info + "',"+ str(status) + ",'"+ ttime +"')"
        result = self.sqlExec(sqlStatement,self.INSERT)
        if result < 0:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "插入log表单失败")

    ##-----------------------------------------------------
    ##获取关键字
    ##-----------------------------------------------------
    def getNewsWebKey(self):
        sqlStatement = "select address,keyword from media.semanteme where class='web'"
        rows = self.sqlExec(sqlStatement,self.SELECT)
        keys = list()
        for row in rows:
            for key in row[1]:
                keys.append(key)
        return keys
    def getWxWbKey(self,tabelName):
        sqlStatement = "select address,keyword,keyescape from media.semanteme where class='"+tabelName+"'"
        rows = self.sqlExec(sqlStatement, self.SELECT)
        keyWordList = list()
        address = list()
        for row in rows:
            keyWord = ""
            address.append(row[0])
            for key in row[1]:
                keyWord += key + " "
            keyWord += "|"
            for key in row[2]:
                keyWord += key + " "
            keyWordList.append(keyWord)
        return address,keyWordList
    # def getWeiboKey(self):
    #     sqlStatement = "select address,keyword,keyescape from media.semanteme where class='weibo'"
    #     rows = self.sqlExec(sqlStatement,self.SELECT)
    #     keyWordList = list()
    #     for row in rows:
    #         keyWord = ""
    #         keyWord += row[0] + " "
    #         for key in row[1]:
    #             keyWord += key + " "
    #         keyWord += "|"
    #         for key in row[2]:
    #             keyWord += key + " "
    #         keyWordList.append(keyWord)
    #     return keyWordList
    ##-----------------------------------------------------
    ##天气数据的保存
    ##-----------------------------------------------------
    def isContainWeatherData(self,station,time,type):
        sqlStatment= "select * from media.webweather%s where ttime='%s' and station='%s'"% (type,time,station)
        result = self.sqlExec(sqlStatment,self.SELECT)
        if len(result) > 0:
            return True
        return False
    def saveWeatherData(self,resultDict,station,type):
        for day in resultDict:
            dayTime = day["time"]
            for data in day["data"]:
                time = dayTime + " " + data["ttime"] + ":00"
                data["ttime"] = time
                if self.isContainWeatherData(station,time,type):
                    dbStatement = "UPDATE media.webweather%s SET " % type
                    valueStr = "WHERE ttime='%s' and station='%s'" % (time,station)
                    self.updateWeatherData(dbStatement,valueStr,data)
                else:
                    dbStatement = "INSERT INTO media.webweather%s ("%type
                    valueStr = "VALUES ("
                    self.insertWeatherData(dbStatement,valueStr,station,data)
        self.saveLogInfo("weather", "天气预报%s天数据抓取完毕"%type, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "天气预报%s天数据抓取完毕  "%type + "运行状态: " + str(1))

    def insertWeatherData(self,dbStatement,valueStr,station,data):
        dbStatement += 'station,'
        valueStr += "'" + station + "'" + ","
        dbStatement += 'tn,'
        valueStr += "'',"
        dbStatement += 'tx,'
        valueStr += "'',"
        dbStatement += 'td,'
        valueStr += "'',"
        for key in data:
            value = data[key]
            dbStatement += key + ","
            valueStr += "'" + str(value) + "',"
        dbStatement = dbStatement[0:len(dbStatement) - 1] + ") "
        valueStr = valueStr[0:len(valueStr) - 1] + ")"
        dbStatement += valueStr
        row = self.sqlExec(dbStatement, self.INSERT)
        if row < 0:
            self.saveLogInfo("weather","天气预报数据插入数据库失败" , datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "天气预报数据插入数据库失败  " + "运行状态: " + str(1))

    def updateWeatherData(self,dbStatement,valueStr,data):
        for key in data:
            dbStatement += key + "="
            dbStatement += "'"+ str(data[key]) +"',"
        dbStatement = dbStatement[0:len(dbStatement)-1]+" "
        dbStatement += valueStr
        result = self.sqlExec(dbStatement,self.INSERT)
        if result < 0:
            self.saveLogInfo("weather", "天气数据更新数据库失败", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "天气数据更新数据库失败  " + "运行状态: " + str(1))

    def saveHistoryData(self,result,tableName):
        dbStatement = "INSERT INTO " + tableName + " ("
        valueStr = "VALUES ("
        for key in result:
            dbStatement += key + ","
            valueStr += "'" + str(result[key]) + "',"
        dbStatement = dbStatement[0:len(dbStatement) - 1] + ") "
        valueStr = valueStr[0:len(valueStr) - 1] + ")"
        dbStatement = dbStatement + valueStr
        result = self.sqlExec(dbStatement, self.INSERT)
        if result < 0:
            self.saveLogInfo("weather", "天气历史数据插入数据库失败", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " weather " + "天气历史数据插入数据库失败  " + "运行状态: " + str(1))

    ##-----------------------------------------------------
    ##AQI数据保存
    ##-----------------------------------------------------
    def isContainAqiData(self,timepoint,positionname):
        sql =  "select * from media.airquality where timepoint='"+timepoint+"' and positionname='"+positionname+"'"
        result = self.sqlExec(sql,self.SELECT)
        if len(result) > 0:
            return True
        else:
            return False
    def saveAqiData(self,aqiDetailJson,dbNameList):
        for aqiDetail in aqiDetailJson:
            if not aqiDetail['position_name']:
                continue
            if self.isContainAqiData(aqiDetail["time_point"],aqiDetail["position_name"]):
                continue
            dbStatement = "INSERT INTO media.airquality ("
            valueStr = "VALUES ("
            for key in aqiDetail:
                tempKey = key
                if key == "position_name":
                    tempKey = "positionname"
                if key == "primary_pollutant":
                    tempKey = "primarypollutant"
                if key == "time_point":
                    tempKey = "timepoint"
                if key == 'no2':
                    tempKey = 'no'
                if key == 'no2_24h':
                    tempKey = 'no_24h'
                if key == 'pm2_5':
                    tempKey='pm25'
                if key == 'pm2_5_24h':
                    tempKey = 'pm25_24h'
                if tempKey in dbNameList:
                    dbStatement += tempKey + ","
                    thisStr = "'"+str(aqiDetail[key])+ "',"
                    if tempKey == "timepoint":
                        thisStr = thisStr.replace('T',' ')
                        thisStr = thisStr.replace('Z','')
                    valueStr += thisStr
            dbStatement = dbStatement[0:len(dbStatement) - 1] + ") "
            valueStr = valueStr[0:len(valueStr) - 1] + ")"
            dbStatement = dbStatement+valueStr
            result = self.sqlExec(dbStatement,self.INSERT)
            if result < 0:
                self.saveLogInfo("aqi", "AQI数据插入数据库失败", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " aqi " + "AQI数据插入数据库失败  " + "运行状态: " + str(1))

    ##-----------------------------------------------------
    ##水质数据的
    ##-----------------------------------------------------
    def saveWater(self,resultList,tableName):
        for result in resultList:
            if len(result) <= 2:
                continue
            dbStatement = "INSERT INTO "+ tableName +" ("
            valueStr = "VALUES ("
            for key in result:
                dbStatement += key + ","
                valueStr += "'"+str(result[key])+"',"
            dbStatement = dbStatement[0:len(dbStatement) - 1] + ") "
            valueStr = valueStr[0:len(valueStr) - 1] + ")"
            dbStatement = dbStatement + valueStr
            result = self.sqlExec(dbStatement, self.INSERT)
            if result < 0:
                self.saveLogInfo("wather", "河流数据插入数据库失败", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wather " + "河流数据插入数据库失败  " + "运行状态: " + str(1))

    def waterLatestTime(self):
        sqlStatment = "select Max(dtime) from media.waterreport "
        result = self.sqlExec(sqlStatment,self.SELECT)
        if len(result) > 0:
            return result[0]
        else:
            return None
    def newsLastestTime(self):
        sqlStatment = "select Max(dtime) from media.news "
        result = self.sqlExec(sqlStatment, self.SELECT)
        if len(result) > 0:
            return result[0]
        else:
            return None
    ##-----------------------------------------------------
    ##新闻数据的保存
    ##-----------------------------------------------------
    def saveNews(self,result,tableName):
        if self.isContainWebData(result["href"]):
            return
        dbStatement = "INSERT INTO " + tableName + " ("
        valueStr = "VALUES ("
        for key in result:
            dbStatement += key + ","
            valueStr += "'" + str(result[key]) + "',"
        dbStatement = dbStatement[0:len(dbStatement) - 1] + ") "
        valueStr = valueStr[0:len(valueStr) - 1] + ")"
        dbStatement = dbStatement + valueStr
        result = self.sqlExec(dbStatement, self.INSERT)
        if result < 0:
            self.saveLogInfo("news", "新闻插入数据库失败", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " news " + "新闻插入数据库失败  " + "运行状态: " + str(1))

    def isContainWebData(self,href):
        sql = "select * from media.news where href='"+href+"'"
        result = self.sqlExec(sql,self.SELECT)
        if len(result) > 0:
            return True
        else:
            return False
    ##-----------------------------------------------------
    ##查询微信微博当前最新时间
    ##-----------------------------------------------------
    def getWxOrWbLastTime(self,dbName):
        sqlStament = "select max(dtime) from %s"%dbName
        rows = self.sqlExec(sqlStament,self.SELECT)
        if len(rows) > 0:
            time = rows[0][0]
            if time != None:
                return time

    ##-----------------------------------------------------
    ##微博微信数据保存
    ##-----------------------------------------------------
    def isContainWxWbData(self,conmment,tableName):
        sqlStament= "select * from %s where comment='%s'"%(tableName,conmment)
        result = self.sqlExec(sqlStament,self.SELECT)
        if len(result) > 0:
            return True
        return False
    def saveWxWb(self,result,tableName):
        if self.isContainWxWbData(result["comment"],tableName):
            return
        result["href"] = self.html2pdf(result["href"])
        dbStatement = "INSERT INTO " + tableName + " ("
        valueStr = "VALUES ("
        for key in result:
            dbStatement += key + ","
            tempStr = str(result[key]).replace("\r\n","")
            tempStr = tempStr.replace("'",'"')
            valueStr += "'" + tempStr + "',"
        dbStatement = dbStatement[0:len(dbStatement)-1] + ") "
        valueStr = valueStr[0:len(valueStr)-1] + ")"
        dbStatement = dbStatement + valueStr
        result = self.sqlExec(dbStatement, self.INSERT)
        if result < 0:
            self.saveLogInfo("wxwb", "微信微博数据插入数据库失败", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微信微博数据插入数据库失败  " + "运行状态: " + str(1))

    ## html转pdf
    def download(self,driver, target_path):
        def execute(script, args):
            driver.execute('executePhantomScript',
                           {'script': script, 'args': args})

        # hack while the python interface lags
        driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')
        # set page format
        # inside the execution script, webpage is "this"
        page_format = 'this.paperSize = {format: "A4", orientation: "portrait" };'
        execute(page_format, [])

        # render current page
        render = '''this.render("{}")'''.format(target_path)
        execute(render, [])
    def html2pdf(self,url):
        phantomjs = os.getcwd()+"/phantomjs/bin/phantomjs"
        driver = webdriver.PhantomJS(executable_path=phantomjs)
        driver.get(url)

        uuidVal = str(uuid.uuid4()) +".pdf"
        pdfFile =  uuidVal
        self.download(driver,pdfFile)
        shutil.move(os.getcwd()+"/"+uuidVal,os.getcwd()+"/pdf")
        return uuidVal