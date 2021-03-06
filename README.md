# PixivDownloader
[Pixiv下载器](https://github.com/neveis/PixivDownloader/releases)

下载P站指定id的插图（包括漫画）。

下载排行榜，可选择排行榜类型，日期，数量（可以选择忽略插图或者漫画）。

使用简介：

首次运行会自动生成`config.json`文件在当前目录下。

使用文本编辑器（记事本等）打开，在引号中填写账号（`userName`），密码（`password`)。保存地址（`downloadPath`）选填，空则保存在当前目录，可填写绝对路径和相对路径。

如：
```
{
    "userID": "test",
    "password": "test",
    "downloadPath": "D:/"
}
```

填写完再次运行程序，登录成功后会在目录下生产`cookies.json`文件。

请注意不要泄露`config.json`和`cookies.json`，否则账号有被窃取风险。

总共有三种模式：

    1.根据插图（漫画）id下载
    2.下载最新的综合排行榜（所有插图和漫画第一页）
    3.自定义下载

```
自定义下载参数设置如下：

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

注：排行榜类型、内容、日期来自于实际的网页地址，因此并不限于上面所提到的，可以观察下实际地址根据所需设置。
```

因为使用到了Windows控制台的API，因此如果不做修改，只支持Windows下使用。相关API封装在`utlis.py`文件中。

使用了PyInstaller打包了可运行程序，[下载地址](https://github.com/neveis/PixivDownloader/releases)。