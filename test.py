import requests
import bs4
import json

user_agent = {'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71'}

def getEPmenu(url): #訪問選集頁面(取得集數清單)
    res = requests.get(url,headers=user_agent).text
    soup = bs4.BeautifulSoup(res,'html.parser')
    epdata = soup.find_all("a",class_="goto-chapter chapter-box text-truncate")
    for i in epdata:
        print("https://www.xgcartoon.com%s\n"%(i.get('href')))

def getResolution(url): #挑選一集之後取得m3u8網址
    res = requests.get(url,headers=user_agent).text
    soup = bs4.BeautifulSoup(res,'html.parser')
    vid = soup.find("iframe").get("src").split('=')[1].split('&')[0]
    #print("https://xgct-video.vzcdn.net/%s/playlist.m3u8"%(vid))
    res = requests.get("https://xgct-video.vzcdn.net/%s/playlist.m3u8"%(vid))
    open("playlist.m3u8","wb").write(res.content)
    f = open("playlist.m3u8","r")
    m3u8list = f.readlines()
    f.close()
    for i in m3u8list:
        if i[0]!='#':
            resolution = i.split('/')[0] #挑最後一個解析度也就是最高的
    return "https://xgct-video.vzcdn.net/%s/%s/video.m3u8"%(vid,resolution)

def search(keyword):
    res = requests.get("https://www.xgcartoon.com/search?q=%s"%(keyword),headers=user_agent).text
    soup = bs4.BeautifulSoup(res,'html.parser')
    searchres = soup.find_all(class_="topic-list-box")
    for i in searchres:
        print(i.find(class_="h3 mb12").text)
        print(i.find("a").get("href").split('/')[2])

def getSubtitles(url):
    res = requests.get(url,headers=user_agent).text
    soup = bs4.BeautifulSoup(res,'html.parser')
    print(soup)

def typefil():
    res = requests.get("https://www.xgcartoon.com/classify?type=*&region=jp&state=*",headers=user_agent).text
    soup = bs4.BeautifulSoup(res,'html.parser')
    soup = soup.find(class_='filter-type')
    
    tag = soup.find_all(class_='btn')
    for i in tag:
        print("%s,%s"%(i.text,i.get("href")))

def filterRes(reg,types):
    res = requests.get("https://www.xgcartoon.com/classify?type=%s&region=%s&state=*&filter=*"%(types,reg),headers=user_agent).text
    soup = bs4.BeautifulSoup(res,'html.parser')
    searchres = soup.find_all(class_="topic-list-box")
    for i in searchres:
        print(i.find(class_="h3 mb12").text)
        print(i.find("a").get("href").split('/')[2])

def haveTWsub(url):
    res = requests.get("https://xgct-video.vzcdn.net/%s/video_info.json"%(url)).text
    vinfo = json.loads(res)
    if len(vinfo['captions']) > 0:
        for i in range(len(vinfo['captions'])):
            if "TW" in vinfo['captions'][i]['srclang']:
                return True
    else:
        return False

#getEPmenu("https://www.xgcartoon.com/detail/dianqishaonvguoyu-dingdang")
#print(getResolution("https://www.xgcartoon.com/user/page_direct?cartoon_id=tianshijianglindaolewoshenbianriyu-liangmu&chapter_id=X6yDcUxEza"))
#search("電器")
#getSubtitles("https://pframe.xgcartoon.com/player.htm?vid=1e99fd32-b3b1-4706-967d-df9c8a3340f3&autoplay=false")
#typefil()
#filterRes("jp","baihe")
haveTWsub("1e99fd32-b3b1-4706-967d-df9c8a3340f3")
haveTWsub("48b6723b-d705-4be9-91d6-6c6478de8964")