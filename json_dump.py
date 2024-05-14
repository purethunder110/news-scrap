from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
import gzip
#content scrapper class import
from content_scrapper import page_scrapper

#number of loop configuration
cycle_time=500

article=page_scrapper()

options = Options()
options.add_argument("--start-maximized")  # Maximizes the browser window
#options.add_argument("--headless") 
driver = webdriver.Chrome(options=options)

url = "https://www.jagran.com/uttar-pradesh/lucknow-city"
driver.get(url)
json_filter_list=[]

for i in range(2,cycle_time):
    print(i)
    # Scroll to the pagination button
    Load_more_button = driver.find_element(By.ID, "pagination-btn")
    driver.execute_script("arguments[0].scrollIntoView(true);", Load_more_button)

    time.sleep(1)

    # Click on the load more button
    Load_more_button.click()
    time.sleep(2)
    api_url:str="https://api.jagran.com/api/jagran/articlesbystatecity/uttar-pradesh/lucknow-city/"+str(i)+"/10"

    #request filtering to api_url
    filtered_requests = [req for req in driver.requests if api_url in req.url]

    for req in filtered_requests:
        #decompressing data that has been recieved. the format is in gzip,deflate and zstb 
        decoding=gzip.decompress(req.response.body)
        #data extraction
        response_data=decoding.decode("utf-8",errors="ignore")
        json_dump=json.loads(response_data)
        backupset=[]
        for newsdata in json_dump:
            id=newsdata["id"]
            url=f"https://www.jagran.com/uttar-pradesh/lucknow-city-{newsdata["webTitleUrl"]}-{id}.html"
            title=newsdata["headline"]
            description=newsdata["summary"]
            body=article.content_scrapper(url)
            data_ofload={
                "id":id,
                "url":url,
                "title":title,
                "body":body,
                "description":description
            }
            json_filter_list.append(data_ofload)
            backupset.append(data_ofload)
        
        with open("backup2/"+str(i)+".json","w",encoding="utf-8") as file:
            json.dump(backupset,file,ensure_ascii=False,indent=4)
    #time.sleep(2)

#cloasing the brouser
driver.quit()

#dumping all data extracted into json
with open("jagran_dataset.json","w",encoding="utf-8") as file:
    json.dump(json_filter_list,file,ensure_ascii=False,indent=4)
