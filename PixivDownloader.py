# encoding: UTF-8
from Pixiv import Pixiv
import os
import sys
import datetime
import getopt

'''
-t [i|r|l]  必须
    i:下载指定id的插图（漫画）
    多个id以空格隔开
    例：-t i 1 2 3
    -t i --dist=D:/ 1 2 3
    如果带其他参数，文件路径要放最后

    l:下载指定id列表文件中的插图（漫画）
    需要填写文件路径，如不填写默认为当前目录下的list.txt文件
    例：-t l D:/list.txt
    如果带其他参数，文件路径要放最后

    r:下载排行榜

    以下参数只用于排行榜（非必须）
    -m 排行榜类型（ranking.php?mode=xxx中xxx部分，不填写默认为daily）
    -c 排行榜内容（content=xxx，不填写为空，即综合排行榜，可选illust和manga）
    -d 排行榜日期（date=xxx，不填写为最新的，格式为YYYYMMDD，例：20170101)
    -p 排行榜指定页（每页50项，排行榜最多10页，可以指定下载某一页）
    --pstart= 指定某页开始（有-p时不生效）
    --pend= 指定某页结束（有-p时不生效）
    例: -t r -c illust -d 20170101 --pstart=1 --pend=5 
        下载2017年1月1日插图排行榜的第1至第5页

以下参数非必须
-l 限制漫画下载页数
-d 指定下载路径（只对当前命令有效）
--override 添加该选项时，会覆盖已经下载的文件，默认为不覆盖
--ignore=[|i|m|im] 忽略id类型
    i:忽略插图
    m:忽略漫画
    im：忽略插图及漫画（相当于全忽略）

例：-t l --dist=D:/pixiv/ --override --ignore=m E:/list.txt
'''


pixiv = Pixiv()

while True:
    print u'[1].下载指定ID插图'.encode(sys.stdout.encoding)
    print u'[2].下载最新综合排行榜'.encode(sys.stdout.encoding)
    print u'[3].自定义下载'.encode(sys.stdout.encoding)
    print u'[q].退出'
    command = raw_input(u'请选择：'.encode(sys.stdout.encoding))
    #command = '3'
    while not command in ('1','2','3','q','Q'):
        command = raw_input(u'无效指令，重新输入:'.encode(sys.stdout.encoding))

    if command in 'qQ':
        break

    if command == '1':
        illustId = raw_input(u'输入插图ID:'.encode(sys.stdout.encoding))
        pixiv.getOriginalImg(illustId)
    elif command == '2':
        date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        downloadPath = os.path.join(pixiv.downloadPath,date)
        pixiv.setDownloadPath(downloadPath)
        iId,mId,order = pixiv.getRankingIdList()
        pixiv.getIdFromList(iId)
        pixiv.getIdFromList(mId,MangaPageLimit=1)
        pixiv.setDownloadPath()
    elif command == '3':

        while True:
            cmd = raw_input(u'输入参数（查看README,输入 q 退出）\n'.encode(sys.stdout.encoding))
            #cmd = '-t r -p 1 -l 1'
            try:
                opts,args = getopt.getopt(cmd.split(),'t:m:c:d:p:l:',['pstart=','pend=','override','ignore=','dist='])
                #print opts,args
                break
            except getopt.GetoptError:
                print u'参数不正确'.encode(sys.stdout.encoding)
        
        if cmd in 'qQ':
            print ''
            continue

        t = None
        m = 'daily'
        c = None
        date = None
        p = None
        l = None
        pstart = 1
        pend = None
        override = False
        ignoreIllust = False
        ignoreManga = False
        dist = None
        for opt,value in opts:
            if opt == '-t':
                t = value
            elif opt == '-m':
                m = value
            elif opt == '-c':
                c = value
            elif opt == '-d':
                date = value
            elif opt == '-p':
                p = int(value)
            elif opt =='-l':
                l = int(value)
            elif opt == '--pstart':
                pstart = int(value)
            elif opt == '--pend':
                pend = int(value)
            elif opt == '--override':
                override = True
            elif opt == '--ignore':
                if 'i' in value:
                    ignoreIllust = True
                if 'm' in value:
                    ignoreManga = True
            elif opt == '--dist':
                dist = value
        for arg in args:
            print arg

        if dist != None:
            pixiv.setDownloadPath(dist)

        if t == 'i':
            pixiv.getIdFromList(args,ignoreIllust,ignoreManga,l,override)
        elif t == 'l':
            if len(args) == 0:
                path = './list.txt'
            else:
                path = args[0]
            with open(path) as f:
                idList = f.read().split('\n')
            pixiv.getIdFromList(idList,ignoreIllust,ignoreManga,l,override)
        elif t == 'r':
            if date == None:
                date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
            downloadPath = os.path.join(pixiv.downloadPath,date)
            pixiv.setDownloadPath(downloadPath)
            iId,mId,order = pixiv.getRankingIdList(m,c,date,p,pstart,pend)
            pixiv.getIdFromList(iId,ignoreIllust,ignoreManga,l,override)
            pixiv.getIdFromList(mId,ignoreIllust,ignoreManga,l,override)
            pixiv.setDownloadPath()

        if dist != None:
            pixiv.setDownloadPath()

    print ''

pixiv.close()