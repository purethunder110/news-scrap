import requests
from bs4 import BeautifulSoup
import html5lib
from celery_worker import new_hindustan_dataset
from datetime import datetime
import time

cycle_timer=0
url="https://www.livehindustan.com/uttar-pradesh/lucknow/news"
new_url=url
#page_iteration=9980
#page_iteration=700
page_iteration=791
headers={
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}
'''
while True:
    if cycle_timer==3:
        cycle_timer=0
        time.sleep(120)
    else:
        cycle_timer+=1
    try:
        data=requests.get(new_url,headers=headers)
        print(f"page={page_iteration}|time={datetime.now()}|url-status={data.status_code}")
        data.encoding="utf-8"
        soup=BeautifulSoup(data.text,features="html5lib")
        json_dump=[]
        json_dump_data=soup.find_all('a',class_="card-sm")
        for i in json_dump_data:
            json_dump.append(str(i))
        filter_linvehindustan_dataset.delay(json_dump)

        page_iteration+=1
        new_url=url+f"-{str(page_iteration)}"
    except Exception as e:
        print(e)
        print("Data Entry----->\n"
              f"page iteration={page_iteration}\n"
              f"current json dump={json_dump} \n")
        exit()


with open("testdump.json","w",encoding="utf=8") as file:
    json.dump(json_dump,file,ensure_ascii=False,indent=4)

'''

while True:
    if cycle_timer==8:
        cycle_timer=0
        time.sleep(10)
    else:
        cycle_timer+=1
    try:
        #time.sleep(0.5)
        data=requests.get(new_url,headers=headers)
        print(f"page={page_iteration}|time={datetime.now()}|url-status={data.status_code}")
        data.encoding="utf-8"
        soup=BeautifulSoup(data.text,features="html5lib")
        json_dump={
            "url":[],
            "title":[],
            "description":[]
        }
        post_data=soup.find_all('a',class_="card-sm")
        for i in post_data:
            #get_url
            
            post_url="https://www.livehindustan.com"+str(i["href"])
            
            #post filters for uttar pradesh
            if str(i["href"])[1:14] != "uttar-pradesh":
                continue
            #post filters for lucknow
            if str(i["href"][15:22]) != "lucknow":
                continue
            
            #getting title
            title_tag=i.find('h2',class_="wdgt-subtitle1")
            try:
                post_title=title_tag.get_text()
            except:
                continue

            #getting description
            description_tag=i.find('p')
            try:
                post_description=description_tag.get_text()
            except:
                continue
            #inserting data
            json_dump["url"].append(post_url)
            json_dump["title"].append(post_title)
            json_dump["description"].append(post_description)

        new_hindustan_dataset.delay(json_dump=json_dump,last_case=len(json_dump["url"]))
        page_iteration+=1
        new_url=url+f"-{str(page_iteration)}"
    except Exception as e:
        print(e)
        print("Data Entry----->\n"
              f"page iteration={page_iteration}\n"
              f"current json dump={json_dump} \n")
        exit()
