from celery import Celery
from database_model import NewsData
from DB_engine import Session_threaded
import requests
from bs4 import BeautifulSoup
import html5lib
import logging
import re
import time

#worker thread
worker_thread=Celery('tasks',broker="amqp://lallan:password@localhost:5672/lallanqueue")

#logging file
logging.basicConfig(level=logging.WARNING,filename='app.log', filemode='a', format='%(process)d - %(levelname)s - %(message)s')
logger=logging.getLogger(__name__)

worker_thread.conf.update(
    worker_concurrency=5,
    task_acks_late=True,
    result_backend="db+postgresql://lallan:123456789@localhost:5432/lallandb",
    timezone="UTC",
    enable_utc=True
)
'''
@worker_thread.task
def add_newsdata(newsID,title,url,body,description):
    newdata=NewsData(newsID=newsID,title=title,url=url,body=body,description=description)
    try:
        current_session=Session_threaded()
        current_session.add(newdata)
        current_session.commit()
    except Exception as e:
        print(e)
        current_session.rollback()
'''
@worker_thread.task(bind=True,max_retries=10,default_retry_delay=60,time_limit=60)
def filter_jagaran_data(self,json_dump):
    all_data=[]
    for newsdata in json_dump:
        id=newsdata["id"]
        url=f"https://www.jagran.com/uttar-pradesh/lucknow-city-{newsdata["webTitleUrl"]}-{id}.html"

        #checking if it exist in database
        with Session_threaded() as check_session:
            check = bool(check_session.query(NewsData).filter_by(url=url).first())
            if check:
                logger.warning(f"{id} found in database, skipping")
                continue
        try:
            title=newsdata["headline"]
            description=newsdata["summary"]
            #body=article.content_scrapper(url)
            html_document=requests.get(url, timeout=20)
            html_document.encoding="utf-8"
            soup=BeautifulSoup(html_document.text,features="html5lib")
            article_content=soup.find('div',class_="articlecontent")
            paras=article_content.find_all('p')
            body=""
            for data in paras[:-1]:
                body+=data.get_text()
            #add_newsdata.delay(newsID=id,title=title,url=url,body=body,description=description)
            newdata=NewsData(newsID=id,title=title,url=url,body=body,description=description)
            all_data.append(newdata)
        except requests.RequestException as e:
            logger.error(f"error fetching url:{url}",exec_info=True)
            self.retry(exc=e) 
        except Exception as e:
            logger.error("error occured",exec_info=True)
            self.retry(exc=e) 
    try:
        with Session_threaded() as current_session:
            current_session.add_all(all_data)
            current_session.commit()
    except Exception as e:
        logger.error(f"error-occureed. Data lost={all_data}",exc_info=True)
        current_session.rollback()
        self.retry(exc=e) 
    

livehindustan_headers={
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

@worker_thread.task(bind=True,max_retries=10,default_retry_delay=30,time_limit=60)
def filter_linvehindustan_dataset(self,json_dump):
    time_loop=1
    all_data=[]
    start_time=time.time()
    for htmldatapart in json_dump:
        case_timer=time.time()
        tag=BeautifulSoup(htmldatapart,"html5lib")
        newsdata=tag.find("a",class_="card-sm")
        #filtering sidebar content
        if str(newsdata["href"])[1:14] != "uttar-pradesh":
            logger.warning("url is not from uttar pradesh, leaving")
            time_loop+=1
            continue
        
        #getting url
        url="https://www.livehindustan.com"+str(newsdata["href"])

        #getting internal id
        pattern = r'/[^/]+/[^/]+-(\d+)\.html$'
        id=re.search(pattern,str(newsdata["href"])).group(1)
        
        #checking if it exist in database
        with Session_threaded() as check_session:
            check = bool(check_session.query(NewsData).filter_by(url=url).first())
            if check:
                logger.warning(f"{id} found in database, skipping")
                time_loop+=1
                continue
        try:
            #getting title
            title_tag=newsdata.find('h2',class_="wdgt-subtitle1")
            title=title_tag.get_text()

            #getting description
            description_tag=newsdata.find('p')
            description=description_tag.get_text()

            #getting body text
            body_html=requests.get(url,headers=livehindustan_headers, timeout=20)
            body_filter=BeautifulSoup(body_html.text,features="html5lib")
            try:
                body_list=body_filter.find("div",class_="stry-bdy")
                body_data=body_list.find_all("p")
                body=""
                for datacase in body_data:
                    body+=datacase.get_text()
            except Exception as e:
                logger.error(e)
                logger.warning(f"url of the data-->{url}")
                body=""
            #create article and andding in list
            newdata=NewsData(newsID=id,title=title,url=url,body=body,description=description)
            all_data.append(newdata)
            logger.info(f"Data for case {time_loop}-->")
            logger.info(f"time taken to execute this occurance:{time.time()-case_timer}")
            logger.info(f"time escaped for full program:{time.time()-start_time}")
            time_loop+=1
        except requests.RequestException as e:
            logger.error(f"error fetching url:{url}",exc_info=True)
            logger.warning("Retrying again")
            self.retry(exc=e) 
        except Exception as e:
            logger.error("error occured",exc_info=True)
            logger.warning("Retrying again")
            self.retry(exc=e)
    try:
        with Session_threaded() as current_session:
            current_session.add_all(all_data)
            current_session.commit()
    except Exception as e:
        logger.error(f"error-occureed. Data lost={all_data}",exc_info=True)
        current_session.rollback()
        self.retry(exc=e) 
    logger.info(f"total time taken for worker to execute={time.time()-start_time}")

@worker_thread.task(bind=True,max_retries=10,default_retry_delay=30,time_limit=60)
def new_hindustan_dataset(self,json_dump,last_case):
    all_data=[]
    for case in range(0,last_case):
        #getting url
        url=json_dump["url"][case]
        
        #checking if it exist in database
        with Session_threaded() as check_session:
            check = bool(check_session.query(NewsData).filter_by(url=url).first())
            if check:
                logger.warning(f"{url} found in database, skipping")
                continue

        #getting body text
        try:
            body_html=requests.get(url,headers=livehindustan_headers, timeout=20)
            body_filter=BeautifulSoup(body_html.text,features="html5lib")
            body_list=body_filter.find("div",class_="stry-bdy")
            body_data=body_list.find_all("p")
            body=""
            for datacase in body_data:
                body+=datacase.get_text()
        except requests.RequestException as e:
            logger.error(f"error fetching url:{url}",exc_info=True)
            logger.warning("Retrying again")
            self.retry(exc=e)
        except:
            logger.warning(f"none body dump-->{url}")
            continue

        #getting internal id
        pattern = r'/[^/]+/[^/]+-(\d+)\.html$'
        id=re.search(pattern,url).group(1)
        
        #getting title
        title=json_dump["title"][case]
        
        #getting description
        description=json_dump["description"][case]
        
        newdata=NewsData(newsID=id,title=title,url=url,body=body,description=description)
        all_data.append(newdata)
    try:
        with Session_threaded() as current_session:
            current_session.add_all(all_data)
            current_session.commit()
    except Exception as e:
        logger.error(f"error-occureed. Data lost={all_data}",exc_info=True)
        current_session.rollback()
        self.retry(exc=e) 