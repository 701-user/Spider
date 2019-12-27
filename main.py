import traceback
class Mainspider():
    def __init__(self,configs):
        from DataLib import Spider
        self.spider = Spider.spider(configs)
    def run(self):
        print("初始化工作")
        self.spider.init()

        self.spider.run()
def testLib():
    try:
        import urllib.request
        import urllib.parse
        from bs4 import BeautifulSoup, NavigableString
        from threading import Thread as thread
        import threading
        from selenium import webdriver
        import psycopg2
        from Crypto.Cipher import AES
        return True
    except Exception as e:
        traceback.print_exc()
        return False
def main():
    configs = {
        "weather": "\\config\\weatherFc.ini",
        "water":"\\config\\waterQuality.ini",
        "aqi": "\\config\\AQI.ini",
        "news":"\\config\\news.ini",
        "db": "\\config\\config.ini"
    }
    print("主入口函数")
    if not testLib():
        print("库包缺失")
    mainSpider = Mainspider(configs)
    mainSpider.run()
main()