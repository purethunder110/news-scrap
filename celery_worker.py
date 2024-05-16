from celery import Celery
from database_model import NewsData
from DB_engine import Session_threaded
import requests
from bs4 import BeautifulSoup
import html5lib
import logging

#worker thread
worker_thread=Celery('tasks',broker="amqp://lallan:password@localhost:5672/lallanqueue")

#logging file
logging.basicConfig(level=logging.WARNING,filename='app.log', filemode='a', format='%(process)d - %(levelname)s - %(message)s')
logger=logging.getLogger(__name__)

worker_thread.conf.update(
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
    
