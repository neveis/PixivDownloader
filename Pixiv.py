# encoding: UTF-8
'''
Author: Pbin
description: 下载P站指定id的插图（包括漫画）
下载排行榜，可选择排行榜类型，日期，数量
可以选择忽略插图或者漫画
指定id 
getOriginalImg(illust_id)
排行榜
getRankingIdList()
'''
import requests
import re
import json
import os
import sys
import threading
from Downloader import Downloader
#import requests.packages.urllib3.util.ssl_
#requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

POST_KEY_URL = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
LOGIN_URL = "https://accounts.pixiv.net/api/login?lang=zh"
# 需要illust_id
MEDIUM_URL = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s'
# 需要illust_id
MANGA_URL = 'https://www.pixiv.net/member_illust.php?mode=manga&illust_id=%s'
# 需要illust_id和page
MANGA_IMG_URL = 'https://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=%s&page=%s'

DAILY_RANKING_URL = 'https://www.pixiv.net/ranking.php?mode=daily'
DAILY_ILLUST_RANKING_URL = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust'
# 需要p和tt
DAILY_RANKING_PAGE_URL = 'https://www.pixiv.net/ranking.php?mode=daily&p=%s&format=json&tt=%s'
DAILY_ILLUST_RANKING_PAGE_URL = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%s&format=json&tt=%s'

#用于验证cookie是否有效
SETTING_URL = 'https://www.pixiv.net/setting_user.php'

RANKING_URL = 'https://www.pixiv.net/ranking.php'
# 获取排行榜所需填的参数
RANKING_REQUEST_PARAMS = {
    'mode': None,
    'content': None,
    'p': None,
    'format': None,
    'tt': None,
    'date': None
}

# 登录时用的header
HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8,ja;q=0.6",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
}

# 下载原始图片用的header，referer要为pixiv相关的地址（一般为跳转前的地址）
IMGHEADERS = {
    'accept': 'image/webp,image/*,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, sdch, br',
    'accept-language': 'zh-CN,zh;q=0.8,ja;q=0.6',
    'referer': 'https://www.pixiv.net',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'
}

DAILY_RANKING_HEADERS = {
    'Host': 'www.pixiv.net',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.pixiv.net/ranking.php?mode=daily',
    'Connection': 'keep-alive'
}

STDOUT_ENCODING = sys.stdout.encoding


class Pixiv():
    def __init__(self):
        # 1.读取配置文件
        if not os.path.exists('./config.json'):
            print u' 没有找到配置文件config.json'.encode(STDOUT_ENCODING)
            print u' 请根据README填写配置文件后再运行'.encode(STDOUT_ENCODING)
            with open('./config.json','w') as f:
                congstr = '{\n\t"userID": "",\n\t"password": "",\n\t"downloadPath": ""\n}'
                f.write(congstr)
            os.system('pause>>nul')
            sys.exit()

        with open('./config.json', 'r') as f:
            config = json.loads(f.read())
        self.userID = config['userID']
        self.password = config['password']
        if config['downloadPath'] == "":
            self.downloadPath = os.getcwd()
        else:
            self.downloadPath = config['downloadPath']

        self.defaultDownloadPath = self.downloadPath

        if not os.path.exists(self.downloadPath):
            os.mkdir(self.downloadPath)

        # 2.读取Cookies
        if os.path.exists('./cookies.json'):
            with open('cookies.json', 'r') as f:
                self.cookies = requests.utils.cookiejar_from_dict(
                    json.loads(f.read()))

            if not self.verifyCookie():
                print(u' 尝试登录'.encode(STDOUT_ENCODING))
                self.login()
            else:
                #中文开头可能会出现乱码（Win10 Creators更新后出现）
                print u' 登陆成功 '.encode(STDOUT_ENCODING)
        else:
            print(u' 尝试登录'.encode(STDOUT_ENCODING))
            self.login()

        # 3.创建下载器
        self.downloader = Downloader(cursorPosX=35)

    def login(self):
        # 1.新建一个会话，便于保持cookies
        session = requests.Session()
        session.headers.update(HEADERS)

        # 2.获取post_key
        try:
            post_key_res = session.get(POST_KEY_URL)
        except requests.exceptions.SSLError:
            post_key_res = session.get(POST_KEY_URL,verify=False)

        pattern = re.compile(r'post_key".*?"(.*?)"')  # post_key value
        post_key = re.findall(pattern, post_key_res.text.encode("utf-8"))[0]

        # 3.登录获取cookies
        formData = {
            'pixiv_id': self.userID,
            'password': self.password,
            'captcha': '',
            'g_recaptcha_response': '',
            'post_key': post_key,
            'source': 'pc',
            'ref': 'wwwtop_accounts_index',
            'return_to': 'https://www.pixiv.net/'
        }
        try:
            login_res = session.post(LOGIN_URL, data=formData)
        except requests.exceptions.SSLError:
            login_res = session.post(LOGIN_URL, data=formData,verify=False)
            
        self.cookies = login_res.cookies

        # 4.保存cookies到文件
        with open('./cookies.json', 'w') as f:
            cookies_str = requests.utils.dict_from_cookiejar(self.cookies)
            f.write(json.dumps(cookies_str))

        print(u' 登录成功'.encode(STDOUT_ENCODING))

    def verifyCookie(self):
        try:
            res = requests.get(SETTING_URL, cookies=self.cookies)
        except requests.exceptions.ConnectionError:
            res = requests.get(SETTING_URL, cookies=self.cookies, verify=False)
        
        if len(res.history):
            res = res.history[0]
        if res.status_code == 200:
            return True
        else:
            return False
            
    # 判断ID是medium还是manga
    def checkType(self, illustId):
        # 1.获取网页
        try:
            res = requests.get(MEDIUM_URL % (illustId), cookies=self.cookies)
        except requests.exceptions.ConnectionError:
            #连接错误重新下载
            self.checkType(illustId)
            return 'ignore',''
        except requests.exceptions.SSLError:
            #SSL错误，不验证方式连接
            res = requests.get(MEDIUM_URL % (illustId), cookies=self.cookies,verify=False)

        mangaPattern = re.compile(r'multiple')
        result = re.findall(mangaPattern, res.text.encode("utf-8"))
        if len(result):
            idType = 'manga'
            url = MANGA_URL % (illustId)
        else:
            mediumPattern = re.compile(
                r'data-src="(.*?)".*?class="original-image"')
            result = re.findall(mediumPattern, res.text.encode("utf-8"))
            if len(result):
                idType = 'medium'
                url = result[0]
            else:
                idType = 'unknow'
                url = ''

        return idType, url

    def getMangaImgUrls(self, pID, mangaUrl, MangaPageLimit=None):
        # 1.获取manga中插图的数量
        try:
            mangaRes = requests.get(mangaUrl, cookies=self.cookies)
        except requests.exceptions.ConnectionError:
            #连接错误重新下载
            self.getMangaImgUrls(pID, mangaUrl, MangaPageLimit)
            return []
        except requests.exceptions.SSLError:
            #SSL错误，不验证方式连接
            mangaRes = requests.get(mangaUrl, cookies=self.cookies,verify=False)

        pattern = re.compile(r'item-container')
        count = len(re.findall(pattern, mangaRes.text))

        # 最大下载数量
        if MangaPageLimit != None:
            if MangaPageLimit < count:
                count = MangaPageLimit

        # 2.构造子图所在的地址
        urls = []
        for i in range(count):
            urls.append(MANGA_IMG_URL % (pID, i))

        # 3.获取原图地址
        imgUrls = []
        for url in urls:
            try:
                res = requests.get(url, cookies=self.cookies)
            except requests.exceptions.ConnectionError:
                #连接错误重新下载
                self.getMangaImgUrls(pID, mangaUrl, MangaPageLimit)
                return []
            except requests.exceptions.SSLError:
                #SSL错误，不验证方式连接
                res = requests.get(url, cookies=self.cookies,verify=False)

            pattern = re.compile(r'"(.*?img-original.*?)"')
            imgUrls.append(re.findall(pattern, res.text.encode('utf-8'))[0])

        return imgUrls

    def downloadManga(self, illustId, imgUrls, override=False):
        for i in range(len(imgUrls)):
            extension = imgUrls[i].split('.')[-1]
            filename = 'pixiv%s_%s.%s' % (illustId, i, extension)
            self.downloadImg(filename, imgUrls[i], override)

    def downloadImg(self, filename, imgUrl, override=False, dir=None):
        # 1.保存路径
        filePath = os.path.join(self.downloadPath, filename)

        # 2.下载
        self.downloader.add(filePath, imgUrl, IMGHEADERS,
                            self.cookies, override)

    def downloadIllust(self, illustId, imgUrl, override=False):
        # 1.生成文件名
        # 文件扩展名
        extension = imgUrl.split('.')[-1]
        # 和手机端命名一致
        filename = 'pixiv%s.%s' % (illustId, extension)
        self.downloadImg(filename, imgUrl, override)

    def getRankingIdList(self, mode='daily', content=None, date=None, page=None, pageStart=1, pageEnd=None):
        # https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%s&format=json&tt=%s
        print u' 读取排行榜'.encode(STDOUT_ENCODING)
        requestParams = RANKING_REQUEST_PARAMS.copy()
        # 1.获取tt
        requestParams['mode'] = 'daily'
        try:
            res = requests.get(RANKING_URL, params=requestParams,
                            headers=DAILY_RANKING_HEADERS, cookies=self.cookies)
        except requests.exceptions.SSLError:
            #SSL错误，不验证方式连接
            res = requests.get(RANKING_URL, params=requestParams,
                            headers=DAILY_RANKING_HEADERS, cookies=self.cookies,verify=False)

        pattern = re.compile(r'pixiv.context.token.*?"(.*?)"')
        tt = re.findall(pattern, res.text)[0]

        # 排行榜最多10页500张
        if pageEnd == None:
            pageEnd = 10
        # 如果指定了page，只下载该page
        if page != None:
            pageStart = pageEnd = page

        # 2.获取排行榜数据
        requestParams['mode'] = mode
        requestParams['content'] = content
        requestParams['tt'] = tt
        requestParams['format'] = 'json'
        requestParams['date'] = date
        illustIdList = []
        mangaIdList = []
        order = {}
        for page in range(pageStart, pageEnd + 1):
            requestParams['p'] = page
            try:
                res = requests.get(RANKING_URL, params=requestParams,
                                headers=DAILY_RANKING_HEADERS, cookies=self.cookies)
            except requests.exceptions.SSLError:
                #SSL错误，不验证方式连接
                res = requests.get(RANKING_URL, params=requestParams,
                                    headers=DAILY_RANKING_HEADERS, cookies=self.cookies,verify=False)

            data = json.loads(res.text)
            for i in range(len(data['contents'])):
                # 页数大于1是图集
                pageCount = int(data['contents'][i]['illust_page_count'])
                if pageCount > 1:
                    mangaIdList.append(data['contents'][i]['illust_id'])
                else:
                    illustIdList.append(data['contents'][i]['illust_id'])
                order[data['contents'][i]['illust_id']] = i

        return illustIdList, mangaIdList, order

    def getIdFromList(self, idList, ignoreIllust=False, ignoreManga=False, MangaPageLimit=None, override=False):
        # 请求速度也较慢，使用多线程
        # 同时最多4个线程
        sem = threading.Semaphore(4)
        threads = []
        # 1.根据override，判断文件是否已存在，manga在这一步无法判断
        for i in range(len(idList)):
            illustId = idList[i]
            # 未知类型和插图，不覆盖的情况下，验证文件是否已存在,存在则跳过
            if override == False:
                pngFileName = 'pixiv%s.png' % (illustId)
                jpgFileName = 'pixiv%s.jpg' % (illustId)
                pngPath = os.path.join(self.downloadPath, pngFileName)
                jpgPath = os.path.join(self.downloadPath, jpgFileName)
                if os.path.exists(pngPath) or os.path.exists(jpgPath):
                    print (u'%s 已存在' % (illustId)).encode(STDOUT_ENCODING)
                    continue

            sem.acquire()
            t = threading.Thread(target=self._getOriginalImgMult, args=(sem, illustId, ignoreIllust,
                                                                        ignoreManga, MangaPageLimit, override))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def _getOriginalImgMult(self, sem, illustId, ignoreIllust=False, ignoreManga=False, MangaPageLimit=None, override=False):
        self.getOriginalImg(illustId, ignoreIllust,
                            ignoreManga, MangaPageLimit, override)
        sem.release()

    def getOriginalImg(self, illustId, ignoreIllust=False, ignoreManga=False, MangaPageLimit=None, override=False):
        idType, url = self.checkType(illustId)
        #print '\r%s' % (illustId),
        if idType == 'medium' and (not ignoreIllust):
            # 下载插图
            self.downloadIllust(illustId, url, override)
        elif idType == 'manga' and (not ignoreManga):
            # 下载合集
            urls = self.getMangaImgUrls(illustId, url, MangaPageLimit)
            self.downloadManga(illustId, urls, override)
        elif idType == 'unknow':
            print (u'%s 未知类型' % (illustId)).encode(STDOUT_ENCODING)
        elif idType == 'ignore':
            pass
        else:
            print (u'%s 忽略' % (illustId)).encode(STDOUT_ENCODING)

    def setDownloadPath(self,downloadPath=None):
        if downloadPath != None:
            self.downloadPath = downloadPath
            if not os.path.exists(downloadPath):
                os.mkdir(downloadPath)
        else:
            self.downloadPath = self.defaultDownloadPath

    def close(self):
        self.downloader.join()
