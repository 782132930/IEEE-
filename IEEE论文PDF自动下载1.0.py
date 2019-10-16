import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import os
from os import path


def getHTMLText(url):
    try:
        r = requests.get(url,timeout=30)#
        r.raise_for_status() #如果状态不是200，引发异常
        r.encoding = 'utf - 8' #无论原来是什么编码，全部改用utf-8
        return r.text
    except:
        return ""
#无界面浏览器设置
def brower_int():
    # 使用headless无界面浏览器模式
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # 增加无界面选项
    chrome_options.add_argument('--disable-gpu')  # 如果不加这个选项，有时定位会出现问题
    #chrome_options.add_argument(r'--user-data-dir=C:\Users\king\AppData\Local\Google\Chrome\User Data')  # 设置成用户自己的数据目录
    return chrome_options
#刷新进度条
def proces_bar(scale,i,t):
    a = '*' * i
    b = '.' * (scale - i)
    c = (i / scale) * 100
    print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c, a, b, -t), end='')
    time.sleep(0.05)

#打开要搜索论文的txt文本
def get_paper_names():
    try:
        fo = open('names.txt','r') #打开names文件
        names=[]
        for line in fo:
            line = line.replace('\n','')
            names.append(line)
        fo.close()
        return names
    except:
        print("names文件打开失败，请检查原因")
#获取要搜索论文的链接
def get_paper_links(names):
    urls=[]
    for name in names:
        url = 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText='+name
        urls.append(url)
    return urls
#selemium获取单个论文编号
def get_paper_nums(browser,url,num=1):#num：爬取单个论文名字的编号个数
    browser.get(url)
    ele_nums = []
    try:
        for link in browser.find_elements_by_xpath("//*[@data-artnum]"):#//*表示无视位置进行遍历，@表示选取元素，@data-artnum即选取元素data-artnum
            if link.get_attribute('className')=='icon-pdf':#这一步是去重
                ele_num = link.get_attribute('data-artnum')
                ele_nums.append(ele_num)
                if len(ele_nums) == num:
                    break
        return ele_nums
    except:
        print("failure")
#获取下载论文的名字
def get_paper_title(ele_nums):
    titles=[]
    print("获取论文名字开始".center(50 // 2, '-'))
    t = time.process_time()
    i=1
    for ele_num in ele_nums:
        url='https://ieeexplore.ieee.org/document/'+ele_num
        html=getHTMLText(url)
        soup=BeautifulSoup(html,'html.parser')
        title=soup.title.string
        titles.append(title)
        t -= time.process_time()
        proces_bar(len(ele_nums), i, t)
        i=i+1
    print("\n" + "获取论文名字结束".center(50 // 2, '-'))
    return titles
#爬取下载链接
def get_download_links(ele_nums):
    srcs=[]
    print("获取论文下载链接开始".center(50 // 2, '-'))
    t = time.time()
    i=1
    for ele_num in ele_nums:
        url = 'https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='+ele_num
        html=getHTMLText(url)
        soup=BeautifulSoup(html,'lxml')#lxml html.parser
        while(soup.find_all('iframe') == []):
            html = getHTMLText(url)
            soup = BeautifulSoup(html, 'lxml')  # lxml html.parser
        src=soup.iframe.attrs['src']
        srcs.append(src)
        proces_bar(len(ele_nums) , i, t-time.time())
        i = i + 1
    print("\n" + "获取论文下载链接结束".center(50 // 2, '-'))
    return srcs
#下载一个大文件
def DownOneFile(srcUrl, localFile):
    # print('%s\n --->>>\n  %s' % (srcUrl, localFile))
    startTime = time.time()
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36','Accept-Encoding': 'gzip, deflate'}
    with requests.get(srcUrl, timeout=80,stream=True,headers=headers) as r:
        contentLength = int(r.headers['content-length'])
        downSize = 0
        with open(localFile, 'wb') as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
                downSize += len(chunk)
                line = '\r%d KB/s - %.2f MB， 共 %.2f MB'
                line = line % (downSize / 1024 / (time.time() - startTime), downSize / 1024 / 1024, contentLength / 1024 / 1024)
                print(line,end='')
                if downSize >= contentLength:
                    break
        timeCost = time.time() - startTime
        line = ' 共耗时: %.2f s, 平均速度: %.2f KB/s'
        line = line % (timeCost, downSize / 1024 / timeCost)
        print(line)
#批量下载pdf文件
def DownFiles(srcUrls,titles):
    print("执行开始".center(50 // 2, '-')+"\n" )
    #创建下载论文目录
    fpath = os.getcwd()  # 获取当前工作目录路径
    fpath = path.join(fpath, '论文')
    if not os.path.isdir('论文'):  # 判断有没有这个文件夹，没有则创建
        os.makedirs(fpath)
    print('总共要下载{}个文件'.format(len(srcUrls)))
    for i in range(len(srcUrls)):
        print('正在下载第{}个文件：{}'.format(i+1,titles[i]))
        filename = path.join(fpath, titles[i] + '.pdf')
        DownOneFile(srcUrls[i], filename)
    print("\n" + "执行结束".center(50 // 2, '-'))

if __name__ == '__main__':
    names=get_paper_names()
    urls=get_paper_links(names)
    browser = webdriver.Chrome(options=brower_int())
    ele_nums=[]
    none_nums=[]
    print("获取论文编码开始".center(50 // 2, '-'))
    t = time.time()
    proces_bar(len(urls), 0, 0)
    for i in range(len(urls)):#获取要下载论文的编号
        ele_num=get_paper_nums(browser, urls[i], 3)
        ele_nums=ele_nums+ele_num
        if len(ele_num) == 0:
            none_nums.append(i)
        proces_bar(len(urls),i+1,t-time.time())
    browser.close()
    print("\n" + "获取下载论文编号结束".center(50 // 2, '-'))
    print(ele_nums)
    for num in none_nums:
        print('{}获取不到论文编码'.format(names[num]))
    # ele_nums = ['7363526', '7363446', '6651558', '6907140', '4650604', '6100821', '1573544', '5679688', '6094415',
    #             '5379537', '6094465', '7041435', '7363506', '7363467']
    srcs = get_download_links(ele_nums)  # ['7363526']
    titles = get_paper_title(ele_nums)
    # ele_nums=['7363526', '7363446', '6651558', '6907140', '4650604', '6100821', '1573544', '5679688', '6094415', '5379537', '6094465', '7041435', '7363506', '7363467']
    # srcs=['https://ieeexplore.ieee.org/ielx7/7349033/7362951/07363526.pdf?tp=&arnumber=7363526&isnumber=7362951&ref=', 'https://ieeexplore.ieee.org/ielx7/7349033/7362951/07363446.pdf?tp=&arnumber=7363446&isnumber=7362951&ref=', 'https://ieeexplore.ieee.org/ielx7/6627393/6651490/06651558.pdf?tp=&arnumber=6651558&isnumber=6651490&ref=', 'https://ieeexplore.ieee.org/ielx7/6895053/6906581/06907140.pdf?tp=&arnumber=6907140&isnumber=6906581&ref=', 'https://ieeexplore.ieee.org/ielx5/4637508/4650570/04650604.pdf?tp=&arnumber=4650604&isnumber=4650570&ref=', 'https://ieeexplore.ieee.org/ielx5/6086637/6100798/06100821.pdf?tp=&arnumber=6100821&isnumber=6100798&ref=', 'https://ieeexplore.ieee.org/ielx5/10507/33272/01573544.pdf?tp=&arnumber=1573544&isnumber=33272&ref=', 'https://ieeexplore.ieee.org/ielx5/5663643/5679617/05679688.pdf?tp=&arnumber=5679688&isnumber=5679617&ref=', 'https://ieeexplore.ieee.org/ielx5/6034548/6094399/06094415.pdf?tp=&arnumber=6094415&isnumber=6094399&ref=', 'https://ieeexplore.ieee.org/ielx5/5368461/5379509/05379537.pdf?tp=&arnumber=5379537&isnumber=5379509&ref=', 'https://ieeexplore.ieee.org/ielx5/6034548/6094399/06094465.pdf?tp=&arnumber=6094465&isnumber=6094399&ref=', 'https://ieeexplore.ieee.org/ielx7/7028729/7041308/07041435.pdf?tp=&arnumber=7041435&isnumber=7041308&ref=', 'https://ieeexplore.ieee.org/ielx7/7349033/7362951/07363467.pdf?tp=&arnumber=7363467&isnumber=7362951&ref=']
    # titles=['Humanoid robot HRP-2Kai — Improvement of HRP-2 towards disaster response tasks - IEEE Conference Publication', "Development of humanoid robot system for disaster response through team NEDO-JSK's approach to DARPA Robotics Challenge Finals - IEEE Conference Publication", 'Identification of the inertial parameters of a humanoid robot using grounded sole link - IEEE Conference Publication', "A summary of team MIT's approach to the virtual robotics challenge - IEEE Conference Publication", 'Humanoid robot HRP-3 - IEEE Conference Publication', 'Humanoid robot that achieves bipedal walk, visual recognition, and multiple finger grasp - IEEE Conference Publication', 'Development of humanoid robot HRP-3P - IEEE Conference Publication', 'Trials of cybernetic human HRP-4C toward humanoid business - IEEE Conference Publication', 'Hardware improvement of Cybernetic Human HRP-4C for entertainment use - IEEE Conference Publication', 'Cybernetic human HRP-4C - IEEE Conference Publication', 'Humanoid robot HRP-4 - Humanoid robotics platform with lightweight and slim body - IEEE Conference Publication', 'Vertical ladder climbing by the HRP-2 humanoid robot - IEEE Conference Publication', 'Task sequencer integrated into a teleoperation interface for biped humanoid robots - IEEE Conference Publication']
    DownFiles(srcs, titles)