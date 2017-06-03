# encoding: UTF-8
import utlis
import threading

class ProgressBar(object):
    def __init__(self,total,info='',finStatus='',length=20,consoleLock=None,cursorPosX=0,cursorPosY=0):
        self.length = length
        self.step = total/length
        self.count = 0
        if len(info) > 20:
            info = info[0:20]
        self.info = info
        self.finStatus = finStatus
        self.consoleLock = consoleLock
        self.cursorPosX = cursorPosX
        self.cursorPosY = cursorPosY

    def refresh(self,count):
        self.count += count
        length = int(self.count/self.step)

        #多线程的情况下需要加锁
        if self.consoleLock != None:
            self.consoleLock.acquire()
            #utlis.SetConsoleCursorPosition(self.cursorPosX,self.cursorPosY)

        #print '\r%-20s['%(self.info) + '|'*length + ' '*(self.length-length) + ']',
        outStr = '%-20s['%(self.info) + '|'*length + ' '*(self.length-length) + ']'
        if length == self.length:
            #print '%+4s'%(self.finStatus)
            outStr += '%+4s'%(self.finStatus)
        else:
            outStr += '%+4s'%(' '*len(self.finStatus))
        utlis.WriteConsoleOutputCharacter(outStr,self.cursorPosX,self.cursorPosY)

        if self.consoleLock != None:
            self.consoleLock.release()
    
    def setTotal(self,total):
        self.step = total/self.length

'''
p = ProgressBar(20,'pixiv62451318','ok')
for i in range(0,20):
    p.refresh(1)
    time.sleep(0.01)
'''

'''
def pro(name,lock,x,y,t):
    p = ProgressBar(20,name,'ok',consoleLock=lock,cursorPosX=x,cursorPosY=y)
    time.sleep(t)
    for i in range(0,20):
        p.refresh(1)
        time.sleep(0.1)

threadLock = threading.Lock()

x,y = utlis.GetConsoleCursorPosition()
t1 = threading.Thread(target=pro,args=('pixiv62451318',threadLock,0,y,0))
t2 = threading.Thread(target=pro,args=('pixiv62451319',threadLock,0,y+1,0.5))

t1.setDaemon(True)
t2.setDaemon(True)
t1.start()
t2.start()

t1.join()
t2.join()
'''
