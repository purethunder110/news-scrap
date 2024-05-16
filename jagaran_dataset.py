from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
import gzip
from celery_worker import filter_jagaran_data
from datetime import datetime
#number of loop configuration
#cycle_time=500

options = Options()
options.add_argument("--start-maximized")  # Maximizes the browser window
#options.add_argument("--headless") 
driver = webdriver.Chrome(options=options)
url = "https://www.jagran.com/uttar-pradesh/lucknow-city"
base_api:str="https://api.jagran.com/api/jagran/articlesbystatecity/uttar-pradesh/lucknow-city/"
driver.get(url)
page_iteration:int=2
session_request=""
while True:
    try:    
        print(f"iteration={page_iteration}| time={datetime.now()}")
        # Scroll to the pagination button
        Load_more_button = driver.find_element(By.ID, "pagination-btn")
        driver.execute_script("arguments[0].scrollIntoView(true);", Load_more_button)
        #time.sleep(1)
        

        # Click on the load more button
        Load_more_button.click()
        if page_iteration !=2:
            session_request=driver.get_cookie("JSESSIONID")
            print(session_request)
        time.sleep(2)

        #create api dynamic url for filtering
        api_url:str=base_api+str(page_iteration)+"/10"

        #request filtering to api_url
        filtered_requests = [req for req in driver.requests if api_url in req.url][0]

        #decompressing data that has been recieved. the format is in gzip,deflate and zstb 
        decoding=gzip.decompress(filtered_requests.response.body)

        #data extraction
        response_data=decoding.decode("utf-8",errors="ignore")
        json_dump=json.loads(response_data)
        
        #sending data to celery worker
        filter_jagaran_data.delay(json_dump)
        page_iteration+=1
    except Exception as e:
        print(e)
        driver.quit()
        print(f"""
              Data_log_entry--->\n
            page_iteration:{page_iteration}\n
            current json_dump:{json_dump}
        """)
        exit()