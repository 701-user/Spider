from threading import Thread as thread
import datetime
class wxwbSpiderInit(thread):
    def __init__(self,wxwb=None,typeNumber=None):
        thread.__init__(self)
        self.type = typeNumber
        if wxwb != None:
            self.wxwbThread = wxwb
    def run(self):
        # type=0表示初始爬取一个月数据
        # type=1表示监听爬取一天的数据
        # type=2表示监听爬取4个月的数据
        self.wxwbThread.conn.saveLogInfo("wxwb", "微信初始化开始", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微信初始化开始  " + "运行状态: " + str(1))
        self.wxwbThread.wx(type=self.type)
        self.wxwbThread.conn.saveLogInfo("wxwb", "微信初始化结束", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微信初始化结束  " + "运行状态: " + str(1))
        self.wxwbThread.conn.saveLogInfo("wxwb", "微博初始化开始", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微博初始化开始  " + "运行状态: " + str(1))
        self.wxwbThread.wb(week=50)
        self.wxwbThread.conn.saveLogInfo("wxwb", "微博初始化结束", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " wxwb " + "微博初始化结束  " + "运行状态: " + str(1))
