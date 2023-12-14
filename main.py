import xbmcplugin, xbmcgui, xbmc, xbmcvfs
import sys
import requests
import bs4
import opencc
import json
import os

temp_PATH = xbmcvfs.translatePath("special://home/").replace("\\","/")+"addons/plugin.video.xgcartoon/temp/"
sys_temp_PATH = xbmcvfs.translatePath("special://temp/").replace("\\","/")

user_agent = {'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71'}

handle=int(sys.argv[1])
dir_level=sys.argv[2].split(")(")

url="www"#sys.argv[0]+'?'+str(dir_level+1)

def haveTWsub(url):
    res = requests.get("https://xgct-video.vzcdn.net/%s/video_info.json"%(url)).text
    vinfo = json.loads(res)
    if len(vinfo['captions']) > 0:
        for i in range(len(vinfo['captions'])):
            if "TW" in vinfo['captions'][i]['srclang']:
                return True
    else:
        return False

def getResolution(ctid,epid): #挑選一集之後取得m3u8網址
    res = requests.get("https://www.xgcartoon.com/user/page_direct?cartoon_id=%s&chapter_id=%s"%(ctid,epid),headers=user_agent).text
    soup = bs4.BeautifulSoup(res,'html.parser')
    vid = soup.find("iframe").get("src").split('=')[1].split('&')[0]
    #print("https://xgct-video.vzcdn.net/%s/playlist.m3u8"%(vid))
    res = requests.get("https://xgct-video.vzcdn.net/%s/playlist.m3u8"%(vid))
    open(temp_PATH+"xgplaylist.m3u8","wb").write(res.content)
    f = open(temp_PATH+"xgplaylist.m3u8","r")
    m3u8list = f.readlines()
    f.close()
    for i in range(len(m3u8list)-1,-1,-1):
        if m3u8list[i][0]!='#':
            resolution = m3u8list[i].split('/')[0]
            #xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?play&',listitem,False)
            listitem = xbmcgui.ListItem(resolution)
            #if haveTWsub(ctid):
            listitem.setSubtitles(["https://xgct-video.vzcdn.net/%s/captions/TW.vtt"%(vid)])
            xbmcplugin.addDirectoryItem(handle,"https://xgct-video.vzcdn.net/%s/%s/video.m3u8"%(vid,resolution),listitem,False)
            
#getResolution("https://www.xgcartoon.com%s"%(i.get('href')))
def getEPmenu(url): #訪問選集頁面(取得集數清單)
    res = requests.get("https://www.xgcartoon.com/detail/%s"%(url),headers=user_agent).text
    soup = bs4.BeautifulSoup(res,'html.parser')
    epdata = soup.find_all("a",class_="goto-chapter chapter-box text-truncate")
    h1title = soup.find("h1",class_="h1").text
    for i in epdata:
        #print("%s\nhttps://www.xgcartoon.com%s\n"%(i.get('title'),i.get('href')))
        #getResolution("https://www.xgcartoon.com%s"%(i.get('href')),i.get('title'))
        listitem = xbmcgui.ListItem(i.get('title'))           #ctid:cartoonID, epid:chapterID
        listitem.setArt({'thumb':'https://static-a.xgcartoon.com/cover/%s.jpg'%(url)})
        xbmcplugin.addDirectoryItem(handle,sys.argv[0]+"?play)(%s)(%s"%(url,i.get('href').split('=')[2]),listitem,True)
        xbmcplugin.setPluginCategory(int(sys.argv[1]), h1title)

def search(keyword):
    res = requests.get("https://www.xgcartoon.com/search?q=%s"%(keyword),headers=user_agent).text
    soup = bs4.BeautifulSoup(res,'html.parser')
    searchres = soup.find_all(class_="topic-list-box")
    for i in searchres:
        #print(i.find(class_="h3 mb12").text)
        listitem = xbmcgui.ListItem(i.find(class_="h3 mb12").text)
        listitem.setArt({'thumb':'https://static-a.xgcartoon.com/cover/%s.jpg'%(i.find("a").get("href").split('/')[2])})
        xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?epmenu)(%s'%(i.find("a").get("href").split('/')[2]),listitem,True)
        #print(i.find("a").get("href").split('/')[2])

def filterRes(reg,types):
    if reg == "all":
        reg = "*"
    if types == "all":
        types = "*"
    res = requests.get("https://www.xgcartoon.com/classify?type=%s&region=%s&state=*&filter=*"%(types,reg),headers=user_agent).text
    soup = bs4.BeautifulSoup(res,'html.parser')
    searchres = soup.find_all(class_="topic-list-box")
    for i in searchres:
        listitem = xbmcgui.ListItem(i.find(class_="h3 mb12").text)
        listitem.setArt({'thumb':'https://static-a.xgcartoon.com/cover/%s.jpg'%(i.find("a").get("href").split('/')[2])})
        xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?epmenu)(%s'%(i.find("a").get("href").split('/')[2]),listitem,True)

if dir_level[0] == "":
    listitem = xbmcgui.ListItem("首頁分類")
    xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?1',listitem,True)
    listitem = xbmcgui.ListItem("輸入影集ID")
    xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?7',listitem,True)
    listitem = xbmcgui.ListItem("搜尋")
    xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?8',listitem,True)
elif dir_level[0] == "?7":
    sfctid = xbmcgui.Dialog().input("直接輸入影集ID")
    getEPmenu(sfctid)
elif dir_level[0] == "?8":
    key_word = xbmcgui.Dialog().input("搜尋")
    key_word = opencc.OpenCC("s2tw").convert(key_word)
    search(key_word)
elif dir_level[0] == "?1":
    listitem = xbmcgui.ListItem("全部")
    xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?2)(all',listitem,True)
    listitem = xbmcgui.ListItem("國漫")
    xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?2)(cn',listitem,True)
    listitem = xbmcgui.ListItem("日本")
    xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?2)(jp',listitem,True)
    listitem = xbmcgui.ListItem("韓國")
    xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?2)(kr',listitem,True)
    listitem = xbmcgui.ListItem("歐美")
    xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?2)(en',listitem,True)
elif dir_level[0] == "?2":
    types = ["全部", "穿越", "科幻", "熱血", "電競", "戰爭", "動作", "驚悚", "災難", "醫療", "成長", 
           "古裝", "友情", "短篇", "少兒", "百合", "真人", "劇情", "推理", "英雄", "懸疑", 
           "人性", "機器", "小劇場", "日常", "蘿莉", "競技", "原創", "可愛", "武俠", "益智", 
           "歷史", "戰鬥", "都市", "總裁", "治癒", "萌系", "修仙", "喜劇", "古風", "神魔", 
           "搞笑", "遊戲改", "高達", "漫畫改", "神話", "仙俠", "戀愛", "恐怖", "軍事", "大女主", 
           "冒險", "兒童向", "早教", "奇幻", "音樂", "運動", "偶像", "學英語", "異世界", "動畫", 
           "料理", "重生", "小說改", "親子", "末日幻想", "少年", "魔法", "少女", "玄幻", "生存", 
           "耽美", "智鬥", "救援", "格鬥", "復仇", "動態漫", "愛情", "後宮", "勵志", 
           "校園", "家庭"]
    argtext = ["all", "chuanyue", "kehuan", "rexue", "dianjing", "zhanzheng", "dongzuo", "jingsong", 
               "zainan", "yiliao", "chengzhang", "guzhuang", "youqing", "duanpian", "shaoer", 
               "baihe", "zhenren", "juqing", "tuili", "yingxiong", "xuanyi", "renxing", "jiqi", 
               "xiaojuchang", "richang", "luoli", "jingji", "yuanchuang", "keai", "wuxia", 
               "yizhi", "lishi", "zhandou", "dushi", "zongcai", "zhiyu", "mengxi", "xiuxian", 
               "xiju", "gufeng", "shenmo", "gaoxiao", "youxigai", "gaoda", "manhuagai", "shenhua", 
               "xianxia", "lianai", "kongbu", "junshi", "danvzhu", "maoxian", "ertongxiang", 
               "zaojiao", "qihuan", "yinyue", "yundong", "ouxiang", "xueyingyu", "yishijie", 
               "donghua", "liaoli", "chongsheng", "xiaoshuogai", "qinzi", "morihuanxiang", 
               "shaonian", "mofa", "shaonv", "xuanhuan", "shengcun", "shenmei", "zhidou", "jiuyuan", 
               "gedou", "fuchou", "dongtaiman", "aiqing", "hougong", "lizhi", 
               "xiaoyuan", "jiating"]
    for i in range(82):
        listitem = xbmcgui.ListItem("%s"%(types[i]))
        xbmcplugin.addDirectoryItem(handle,sys.argv[0]+'?filter)(%s)(%s'%(dir_level[1],argtext[i]),listitem,True)
elif dir_level[0] == "?filter":
    filterRes(dir_level[1],dir_level[2])
elif dir_level[0] == "?epmenu":
    getEPmenu("%s"%(dir_level[1]))
elif "?play" in dir_level[0]:
    getResolution(dir_level[1],dir_level[2])

#xbmcgui.Dialog().ok("info","%s"%(dir_level))
#xbmcgui.Dialog().ok("info","%s\n%s\n%s"%(sys.argv[0],sys.argv[2],sys.argv[1]))
xbmcplugin.endOfDirectory(handle)
