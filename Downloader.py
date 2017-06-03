# encoding: UTF-8
from ProgressBar import ProgressBar
import requests
from contextlib import closing
import threading
import Queue
import utlis
import os
import sys

class Downloader():
    def __init__(self, maxThreadNum=5,cursorPosX=None,cursorPosY=None):
        self.setCursorPos(cursorPosX,cursorPosY)
        self.printSlotQue = Queue.Queue()
        self.createPrintSlot(maxThreadNum)

        self.exitFlag = False
        self.consoleLock = threading.Lock()
        self.urlQueue = Queue.Queue()
        self.threadSem = threading.Semaphore(maxThreadNum)
        self.cursorLock = threading.Lock()
        self.threads = []
        self.runMethodThread = threading.Thread(target=self.run, args=())
        self.runMethodThread.start()
        self.totalTask = 0
        self.taskCount = 0
        self.updateCount()

    def totalTaskInc(self):
        self.totalTask +=1
        self.updateCount()
    
    def taskCountInc(self):
        self.taskCount +=1
        self.updateCount()

    def updateCount(self):
        outStr = '(%s/%s)      '%(self.taskCount,self.totalTask)
        utlis.WriteConsoleOutputCharacter(outStr,self.cursorPosX,self.cursorPosY)

    def add(self, filePath, url, headers, cookies, override=False):
        # 将待下载的相关信息存到队列中,不一定会马上下载
        urlobj = {
            'filePath': filePath,
            'url': url,
            'headers': headers,
            'cookies': cookies,
            'override': override
        }
        self.totalTaskInc()
        self.urlQueue.put(urlobj)

    def download(self, filePath, url, headers, cookies, cursorPosY, override=False):

        fileName = os.path.basename(filePath)
        # 1.创建进度条,total连接上后再设置
        # 1.1.如果不覆盖且文件以存在，不下载
        if (not override) and os.path.exists(filePath):
            pb = ProgressBar(20, fileName, 'ok',
                             consoleLock=self.consoleLock, cursorPosX=self.cursorPosX, cursorPosY=cursorPosY)
            pb.refresh(20)
            self.taskCountInc()
        else:
            pb = ProgressBar(20, fileName, 'ok',
                             consoleLock=self.consoleLock, cursorPosX=self.cursorPosX, cursorPosY=cursorPosY)
            pb.refresh(0)
            # 2.流形式请求 超时未验证是否有效
            try:
                with closing(requests.get(url, headers=headers, cookies=cookies, stream=True,timeout=(6,30))) as res:
                    dataLength = int(res.headers['content-length'])
                    pb.setTotal(dataLength)

                    with open(filePath, 'wb') as fd:
                        # 3.保存数据
                        for data in res.iter_content(chunk_size=51200):
                            fd.write(data)
                            # 4.更新进度条
                            pb.refresh(len(data))
                    
                self.taskCountInc()
            except requests.exceptions.Timeout:
                print (u'%s 超时' % (fileName)).encode(sys.stdout.encoding)
                if os.path.exists(filePath):
                    os.remove(filePath)
                urlobj = {
                    'filePath': filePath,
                    'url': url,
                    'headers': headers,
                    'cookies': cookies,
                    'override': override
                }
                self.urlQueue.put(urlobj)
            except requests.exceptions.ConnectionError,requests.exceptions.SSLError:
                with closing(requests.get(url, headers=headers, cookies=cookies, stream=True,timeout=(6,30),verify=False)) as res:
                    dataLength = int(res.headers['content-length'])
                    pb.setTotal(dataLength)

                    with open(filePath, 'wb') as fd:
                        # 3.保存数据
                        for data in res.iter_content(chunk_size=51200):
                            fd.write(data)
                            # 4.更新进度条
                            pb.refresh(len(data))
                    
                self.taskCountInc()
        
        self.printSlotQue.put(cursorPosY)
        # 5.释放多线程信号量
        self.threadSem.release()

    def run(self):
        # 一直运行
        while True and (not (self.exitFlag and self.urlQueue.empty())):
            # 获取下载信息
            try:
                # 设置超时，方便退出
                urlObj = self.urlQueue.get(block=True, timeout=1)
                # 线程信号量，控制线程数量
                self.threadSem.acquire()
                cursorPosY = self.printSlotQue.get()
                t = threading.Thread(target=self.download, args=(
                    urlObj['filePath'], urlObj['url'], urlObj['headers'], urlObj['cookies'], cursorPosY, urlObj['override']))
                self.threads.append(t)
                t.start()
            except Queue.Empty:
                continue

    def setCursorPos(self,cursorPosX=None,cursorPosY=None):
        x, y = utlis.GetConsoleCursorPosition()
        if cursorPosX != None:
            self.cursorPosX = cursorPosX
        else:
            self.cursorPosX = x

        if cursorPosY != None:
            self.cursorPosY = cursorPosY
        else:
            self.cursorPosY = y

    def createPrintSlot(self,count):
        for dy in range(1,count + 1):
            self.printSlotQue.put(self.cursorPosY + dy)

    def setCursorPosY(self):
        self.cursorLock.acquire()
        if self.cursorPosY == None:
            x, y = utlis.GetConsoleCursorPosition()
            self.cursorPosY = y
        self.cursorLock.release()

    def getCursorPosY(self):
        self.cursorLock.acquire()
        if self.cursorPosY == None:
            return None
        y = self.cursorPosY
        self.cursorPosY += 1
        self.cursorLock.release()
        return y

    def join(self):
        # 等待各线程结束
        self.exitFlag = True
        self.runMethodThread.join()
        for t in self.threads:
            t.join()
        self.exitFlag = False
