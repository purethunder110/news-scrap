import requests
import html5lib
from bs4 import BeautifulSoup

class page_scrapper:
    
    def __init__(self) -> None:
        pass

    def content_scrapper(self,url):
        html_document=requests.get(url)
        html_document.encoding="utf-8"
        soup=BeautifulSoup(html_document.text,features="html5lib")
        article_content=soup.find('div',class_="articlecontent")
        paras=article_content.find_all('p')
        body=""
        for data in paras[:-1]:
            body+=data.get_text()
        return body


if __name__=="__main__":
    test=page_scrapper()
    data=test.content_scrapper("https://www.jagran.com/uttar-pradesh/lucknow-city-if-police-asks-then-tell-them-criminal-with-a-reward-of-rs-50000-had-brainwashed-his-wife-caught-by-sog-team-23715017.html")
    print(data)