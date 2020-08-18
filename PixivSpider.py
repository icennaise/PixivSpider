
# -*- coding: utf-8 -*-
import os
import requests
import re
import time
import zipfile
def file_name(file_dir):
    L=[]
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            L.append(file.split(".")[0])#当前路径下所有非目录子文件
    return L
path=("download")#如果目录下不存在download文件夹则创建此文件夹
isExists=os.path.exists(path)
if not isExists:
        os.makedirs(path) 
downloaded=file_name("download")#返回已下载过的文件名防止重复下载
inter_url="https://www.pixiv.net/member_illust.php?mode=medium&illust_id="
loginHeader = { 
       'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
       'Referer': "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
       'cookie':"__cfduid=db0a0c316c591aa11e4f7cd103d2f4d5f1597729530; first_visit_datetime_pc=2020-08-18+14%3A45%3A30; p_ab_id=8; p_ab_id_2=0; p_ab_d_id=834985689; yuid_b=J3GAlCM; __utma=235335808.709683855.1597729532.1597729532.1597729532.1; __utmc=235335808; __utmz=235335808.1597729532.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _fbp=fb.1.1597729532642.1869815081; login_bc=1; _ga=GA1.2.709683855.1597729532; _gid=GA1.2.606048055.1597729535; device_token=5109b960e6a7d35a048a259228c29b51; c_type=23; a_type=0; b_type=1; __utmv=235335808.|2=login%20ever=no=1^3=plan=normal=1^5=gender=male=1^6=user_id=20252417=1^9=p_ab_id=8=1^10=p_ab_id_2=0=1^11=lang=zh=1; tag_view_ranking=RTJMXD26Ak~pYlUxeIoeg~28gdfFXlY7~cbmDKjZf9z~Ie2c51_4Sp~n7YxiukgPF~jH0uD88V6F~hzLsBUtKYm~Ap7SN6vi86~v_vD9SVa8E~1GBicHu4Rs~BtXd1-LPRH~HY55MqmzzQ~xb-vAio_xa~tgP8r-gOe_~GlEsKjRIS3~Lt-oEicbBr~RybylJRnhJ~2acjSVohem~p1cqF95SSS~Fq4K_8PGib~ThlAk1fdQu~m3EJRa33xU~uW5495Nhg-~5Npf-yb62j~S0eWMRWoH6~DHJKxWnZVV~6QVzqxQeU8~HSgaEGfNA1~xXK363-v9t~t2ErccCFR9~e8ijvNyzrI~Jt2j1jdIC3~zIv0cf5VVk~xlnbe0hAbx; ki_t=1597729541065%3B1597729541065%3B1597731041679%3B1%3B6; __utmt=1; __utmb=235335808.30.10.1597729532; _gat=1; PHPSESSID=20252417_RT5NgyZwD0miYMRSwWzNcwO96DK3uaNS; privacy_policy_agreement=1"
       }
#proxies = { "http": "http://127.0.0.1:8123", "https": "http://127.0.0.1:8123", } 
proxies = None
LoginUrl = "https://accounts.pixiv.net/api/login?lang=zh"
s=requests.Session()
s.headers=loginHeader
a=s.get("https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",proxies=proxies)
partten='ue="([0-9]*|[a-z])*"'
#postkey=re.findall(r'value="[^"]*',a.text)[0].split('"')[1]
try:#读取目录下的用户信息，若未找到则提示输入用户名和密码
    with open('text.txt', 'r') as f:
        user_name=f.readline()
        password=f.readline()
        user_name=user_name.rstrip("\n")
except(FileNotFoundError) as e:
    user_name=input("输入用户名:")
    password=input('输入密码:')
    with open('text.txt', 'w') as f:
        f.write(user_name)
        f.write("\n")
        f.write(password)
data={
    'password': password,
    'pixiv_id': user_name,
    #'post_key': postkey,
    'return_to': 'https://www.pixiv.net/'
    }
b=s.post(LoginUrl,data=data,headers=loginHeader,proxies=proxies)
print(b.text)
aim_url_p="https://www.pixiv.net/ajax/illust/70449747/recommend/init?limit="
aim_url_p="https://www.pixiv.net/ajax/illust/"
aim_pid=input("输入目标图pid:")
aim_url_f="/recommend/init?limit="
#aim_range=input("设定搜索广度：")
aim_range=35#此参数代表搜索广度，建议范围在20至150之前，会影响所能找到的图片
pattern=re.compile(r'data-id="[1-9][0-9]{4,}')
patternx=re.compile(r'img-original\\/img\\/[0-9][0-9][0-9][0-9]\\/[0-9][0-9]\\/[0-9][0-9]\\/[0-9][0-9]\\/[0-9][0-9]\\/[0-9][0-9]\\/[0-9]{7,}_p0.[p|j|g][n|p|i][f|g]')
patterngif=re.compile(r'/img\\/[0-9][0-9][0-9][0-9]\\/[0-9][0-9]\\/[0-9][0-9]\\/[0-9][0-9]\\/[0-9][0-9]\\/[0-9][0-9]\\/[0-9]{8,}_ugoira0.[p|j][n|p]g')
patterna=re.compile(r'workId":"[0-9]{8,}')
pattermu=re.compile(r'pageCount":[^,]*')
pidx=[aim_pid]
def setPidx(aim_pid):#设定pidx队列，使得爬虫能够不断爬取图片
    #time.sleep(3)
    aim_img_url=aim_url_p+str(aim_pid)+aim_url_f+str(aim_range)
    try:
        #print("try pidx")
        aim_img=s.get(aim_img_url,proxies=proxies)
        #print("set pidx")
        pid=patterna.findall(aim_img.text)
        for i in range(len(pid)):
            if((pid[i].split(':"')[1]) in downloaded or (pid[i].split(':"')[1]) in pidx):
                pass
            else:
                pidx.append((pid[i].split(':"')[1]))
    except(Exception) as e:
        print(e)
        print("0x")
    


def save(text, filename='temp', path='download'):#存储图片
    fpath = os.path.join(path, filename)
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path) 
    with open(fpath, 'wb+') as  f:
        print('output:', fpath)
        f.write(text)
    #if("zip" in filename):
    #    f=zipfile.ZipFile(fpath,'r')
    #    for file in f.namelist():
    #        f.extract(file,"temp\\")
def download(img_url,pid,inner_url,page_count):#根据不同的图片类型使用对应的操作处理图片url
    if("jpg" in img_url):
        te=".jpg"
    elif("png" in img_url):
        te=".png"
    elif("gif" in img_url):
        te=".gif"
    else:
        te=".zip"
    downloadheader={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
       'Referer': inner_url,
        }
    try:
        a=s.get(img_url,proxies=proxies,headers=downloadheader)
        #print("get img")
        b=a.content
        if(page_count==0):
            save(b,str(pid)+te)
            #print("save img")
        elif(page_count==-1):
            save(b,str(pid)+"_p0"+te,"download\\"+str(pid))
            #print("save img")
        else:
            save(b,str(pid)+"_p"+str(page_count)+te,"download\\"+str(pid))
            #print("save img")
    except(requests.exceptions.ProxyError) as e:
        print(e)
        print("1x")
        download(img_url,pid,inner_url,page_count)
def getpic(pid):#根据pid获取图片信息并下载
    print(pid)
    if(im_num<int(imp_limit)):
        setPidx(pid)
    inner_url=inter_url+str(pid)
    #print("getpid")
    try:
        ima=s.get(inner_url,proxies=proxies)
        #print("geturl")
        a=patternx.findall(ima.text)
        b=pattermu.findall(ima.text)
        if(len(b)!=0):
            page_count=b[-1]
            page_count=page_count.split(":")[-1]
            if(int(page_count)!=1):
                print("将要爬取多图")
        else:
            print("获取page出错")
        if(len(a)!=0):
            img_url="https://i.pximg.net/"+a[0].translate(str.maketrans('','','\\'))
        if(len(a)==0):
            a=patterngif.findall(ima.text)
            img_url="https://i.pximg.net/img-zip-ugoira/"+a[0].translate(str.maketrans('','','\\')).split("_")[0]+"_ugoira1920x1080.zip"
        a[0].translate(str.maketrans('','','\\'))
        #print(img_url)
        if(int(page_count)==1):
            download(img_url,pid,inner_url,0)
            #print("try download")
        else:
            download(img_url,pid,inner_url,-1)
            #print("try download")
            for i in range(int(page_count)-1):
                old="_p"+str(i)
                new="_p"+str(i+1)
                img_url=img_url.replace(old,new)
                download(img_url,pid,inner_url,i+1)
    except(Exception) as e:
        print(e)
        print("不断出现此错误可能是账号密码错误或pid不存在")
        getpic(pid)
        #print("retry getpic")
    #time.sleep(3)
setPidx(aim_pid)
imp_limit=input("输入期望爬取的图片数量：")
im_num=0
for i in pidx:
    if(im_num<int(imp_limit)):
        getpic(i)
        im_num+=1
        print("没出错的话这应该是第%d张图"%(im_num))
        print("队列中待爬的图片有%d张"%(len(pidx)))