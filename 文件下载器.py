# encoding: utf-8
# author: walker
# date: 2018-06-11
# summary: 使用 requests 下载大文件
import urllib
import time
import requests

def TexProgress_bar():
    scale = 50
    print("执行开始".center(scale // 2, '-'))
    t = time.process_time()
    for i in range(scale + 1):
        a = '*' * i
        b = '.' * (scale - i)
        c = (i / scale) * 100
        t -= time.process_time()
        print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c, a, b, -t), end='')
        time.sleep(0.05)
    print("\n" + "执行结束".center(scale // 2, '-'))
def download(srcUrl, localFile):
    urllib.urlretrieve(srcUrl, localFile)
# 下载一个大文件
def DownOneFile(srcUrl, localFile):
    print('%s\n --->>>\n  %s' % (srcUrl, localFile))

    startTime = time.time()
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0,Accept-Encoding: gzip, deflate'}
    with requests.get(srcUrl, stream=True,headers=headers) as r:
        contentLength = int(r.headers['content-length'])
        print(r.headers)
        print(contentLength)
        line = 'content-length: %dB/ %.2fKB/ %.2fMB'
        line = line % (contentLength, contentLength / 1024, contentLength / 1024 / 1024)
        print(line)
        downSize = 0
        with open(localFile, 'wb') as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
                downSize += len(chunk)
                line = '\r%d KB/s - %.2f MB， 共 %.2f MB' #\r的作用是不换行覆盖输出
                line = line % (downSize / 1024 / (time.time() - startTime), downSize / 1024 / 1024, contentLength / 1024 / 1024)
                print(line,end='')
                if downSize >= contentLength:
                    break
            f.close()
        timeCost = time.time() - startTime
        line = '\n共耗时: %.2f s, 平均速度: %.2f KB/s'
        line = line % (timeCost, downSize / 1024 / timeCost)
        print(line)


if __name__ == '__main__':
    srcUrl = r'http://cachefly.cachefly.net/100mb.test'
    #srcUrl =r'https://ieeexplore.ieee.org/ielx7/7349033/7362951/07363526.pdf?tp=&arnumber=7363526&isnumber=7362951&ref='
    localFile = r'C:\Users\king\Desktop\out.pdf'
    DownOneFile(srcUrl, localFile)

