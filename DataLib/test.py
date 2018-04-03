from threading import Thread as thread
import traceback
import time
import threading
import urllib.request as urlRequest
class threadOne(thread):
    def __init__(self):
        thread.__init__(self)
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
    def run(self):
        try:
            while self.__running.isSet():
                self.__flag.wait()
                print("a")
                print("b")
                time.sleep(100)
        except Exception as e:
            traceback.print_exc()
threadone = threadOne()
threadone.start()
while True:
    if not threadone.is_alive():
        print("tread is die")
        threadone.stop()
        threadone.setDaemon(True)
        threadone = threadOne()
        threadone.start()
    time.sleep(5)

