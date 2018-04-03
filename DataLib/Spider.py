from DataLib import Weather
from DataLib import Water
from DataLib import Aqi
from DataLib import DataBase
from DataLib import News
from DataLib import Wxwb
import time
import datetime
import traceback
from DataLib import wxwbSpiderInit
class spider():
    def __init__(self,configs):
        self.config = configs
        self.initDB(configs)
        self.netFlag = False
        while not self.netTest():
            time.sleep(200)

        self.spiderList = list()

        self.weather = Weather.weather(configs["weather"],self.dataBase)
        self.weather.setName("weather")

        self.water = Water.water(configs["water"],self.dataBase)
        self.water.setName("water")

        self.aqi = Aqi.aqi(configs["aqi"],self.dataBase)
        self.aqi.setName("aqi")

        self.wxwb = Wxwb.wxwb(configs["db"],self.dataBase)
        self.wxwb.setName("wxwb")

        self.news = News.new(configs["news"],self.dataBase)
        self.news.setName("news")



        self.spiderList.append(self.weather)
        self.spiderList.append(self.water)
        self.spiderList.append(self.aqi)
        self.spiderList.append(self.wxwb)
        self.spiderList.append(self.news)

    def netTest(self):
        import os
        net_state = os.system("ping www.baidu.com")
        if net_state:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" main "+ "网络不连通，请连接网线  " + "运行状态: " + str(1))
            self.dataBase.saveLogInfo("main", "网络不连通，请连接网线", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            return False
        else:
            self.dataBase.saveLogInfo("main", "网络状态良好", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " main " + "网络状态良好  " + "运行状态: " + str(1))
            return True
    def init(self):
        print("读取配置")
        self.spiderThreadList = list()
        for spider in self.spiderList:
            spider.loadConf()
            self.spiderThreadList.append(spider)
        while not self.testBfRun():
            time.sleep(1200)
        ## 初始化微博微信内容
        self.wxwbInit()
    def testBfRun(self):
        ## 运行前的测试 包括配置文件是否存在
        ## 配置文件包括项目文件夹config下的AQI.ini,new.ini,waterQuality.ini,weather.ini等文件
        import os
        dirPath = os.getcwd()
        configDir = dirPath+"/"+ "config"
        if  os.path.exists(configDir):
            AQIpath = configDir +"/"+"AQI.ini"
            if not os.path.exists(AQIpath):
                self.dataBase.saveLogInfo("main", "配置文件夹丢失初始化失败，请确定配置文件AQI.ini是否存在",
                                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " main " + "配置文件夹丢失初始化失败，请确定配置文件AQI.ini是否存在  " + "运行状态: " + str(1))

                return False
            newsPath = configDir + "/"+"news.ini"
            if not os.path.exists(newsPath):
                self.dataBase.saveLogInfo("main", "配置文件夹丢失初始化失败，请确定配置文件news.ini是否存在",
                                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " main " + "配置文件夹丢失初始化失败，请确定配置文件news.ini是否存在  " + "运行状态: " + str(1))

                return False
            waterQualityPath = configDir + "/" + "waterQuality.ini"
            if not os.path.exists(waterQualityPath):
                self.dataBase.saveLogInfo("main", "配置文件夹丢失初始化失败，请确定配置文件waterQuality.ini是否存在",
                                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " main " + "配置文件夹丢失初始化失败，请确定配置文件waterQuality.ini是否存在  " + "运行状态: " + str(1))

                return False
            weatherFcPath = configDir + "/" + "weatherFc.ini"
            if not os.path.exists(weatherFcPath):
                self.dataBase.saveLogInfo("main", "配置文件夹丢失初始化失败，请确定配置文件weatherFc.ini是否存在",
                                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " main " + "配置文件夹丢失初始化失败，请确定配置文件weatherFc.ini是否存在  " + "运行状态: " + str(1))

                return False


            return True
        else:
            self.dataBase.saveLogInfo("main", "配置文件夹丢失初始化失败，请确定项目文件夹下配置文件夹config是否存在",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
            print(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " main " + "配置文件夹丢失初始化失败，请确定项目文件夹下配置文件夹config是否存在  " + "运行状态: " + str(1))
            return False
    def wxwbInit(self):
        # 查询当前时间点和数据库中的时间点，判断是否需要初始化微信和微博
        nowTime = datetime.datetime.now()
        weixinTime = self.dataBase.getWxOrWbLastTime("media.weixin")
        if weixinTime:
            day = (nowTime - weixinTime).days
            # 时间间隔超过5天
            if day >= 3 and day <= 10:
                self.dataBase.saveLogInfo("main", "微信微博需要初始化一个月",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " main " + "微信微博需要初始化一个月  " + "运行状态: " + str(1))
                try:
                    wxwbInit = wxwbSpiderInit.wxwbSpiderInit(self.wxwb,0)
                    wxwbInit.start()
                except Exception as e:
                    exString = ""
                    for arg in e.args:
                        exString += arg
                    exString += traceback.format_exc()
                    self.dataBase.saveLogInfo("main", "微信微博初始化异常 %s"%exString, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " main " + "微信微博初始化异常 %s   "%exString + "运行状态: " + str(1))
            elif day > 10:
                self.dataBase.saveLogInfo("main", "微信微博需要初始化四个个月", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                          1)
                print(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " main " + "微信微博需要初始化四个月  " + "运行状态: " + str(1))
                try:
                    wxwbInit = wxwbSpiderInit.wxwbSpiderInit(self.wxwb,2)
                    wxwbInit.start()
                except Exception as e:
                    exString = ""
                    for arg in e.args:
                        exString += arg
                    exString += traceback.format_exc()
                    self.dataBase.saveLogInfo("main", "微信微博初始化异常 %s" % exString,
                                              datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " main " + "微信微博初始化异常 %s   " % exString + "运行状态: " + str(1))

    # 数据库初始化
    def initDB(self,configs):
        self.dataBase = DataBase.dataBase(configs["db"])
        self.dataBase.loadConfig()
    def getThread(self,name):
        if name == "weather":
            return Weather.weather(self.config["weather"],self.dataBase)
        if name == "water":
            return Water.water(self.config["water"],self.dataBase)
        if name == "aqi":
            return Aqi.aqi(self.config["aqi"],self.dataBase)
        if name == "wxwb":
            return Wxwb.wxwb(self.config["db"],self.dataBase)
        if name == "news":
            return News.new(self.config["news"],self.dataBase)
    def run(self):
        self.dataBase.saveLogInfo("main","主线程开始运行",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " main " + "主线程开始运行  " + "运行状态: " + str(1))

        for spiderThread in self.spiderThreadList:
           spiderThread.start()
        while True:
            if self.netTest():
                if self.netFlag:
                    self.dataBase.saveLogInfo("main", "网络连通，所有线程唤醒",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    ## 判断微信微博中数据是否需要恢复
                    self.wxwbInit()
                    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " main " + "网络连通，所有线程唤醒  " + "运行状态: " + str(1))

                    for spiderThread in self.spiderThreadList:
                        spiderThread.resume()
                    self.netFlag = False
                else:
                    for i,spiderThread in enumerate(self.spiderThreadList):
                        if spiderThread.is_alive():
                            self.dataBase.saveLogInfo(spiderThread.getName(), "线程检测运行良好", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),1)
                            print(datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S") + " " + spiderThread.getName() + " 线程检测运行良好  " + "运行状态: " + str(1))
                        else:
                            spiderThread.getException()
                            spiderThread.stop()
                            spiderThread.join()
                            name = spiderThread.getName()
                            self.spiderThreadList[i] = self.getThread(name)
                            self.spiderThreadList[i].setName(name)
                            self.spiderThreadList[i].loadConf()
                            self.dataBase.saveLogInfo(self.spiderThreadList[i].getName(), "线程异常,重新启动",
                                                      datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
                            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + self.spiderThreadList[i].getName() + " 线程异常,重新启动  " + "运行状态: " + str(0))

                            self.spiderThreadList[i].start()
                    self.dataBase.saveLogInfo("main", "sleep 20分钟之后所有子线程检测运行状态",
                                              datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " main " + " sleep 20分钟之后所有子线程检测运行状态  " + "运行状态: " + str(1))
            else:
                if not self.netFlag:
                    self.dataBase.saveLogInfo("main", "网络不通所有线程暂停",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " main " + "网络不通所有线程暂停  " + "运行状态: " + str(1))
                    for spiderThread in self.spiderThreadList:
                        spiderThread.pause()
                    self.netFlag = True
                else:
                    self.dataBase.saveLogInfo("main", "所有线程暂停中.....",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
                    print(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " main " + "所有线程暂停中.....  " + "运行状态: " + str(1))
            if not self.dataBase.testConnecting():
                self.dataBase.connectDB()
                self.dataBase.saveLogInfo("main", "重置数据库连接", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),1)
                print(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " main " + "重置数据库连接  " + "运行状态: " + str(1))
                for spiderThread in self.spiderThreadList:
                    spiderThread.dbReset(self.dataBase)
            time.sleep(1200)
