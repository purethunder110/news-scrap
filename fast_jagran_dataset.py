import requests
import json
from celery_worker import filter_jagaran_data
from datetime import datetime
import time
sleep_counter=0
page_iteration:int=2
payload={"Authorization":"Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJqYWdyYW5uZXdtZWRpYSIsImlhdCI6MTY4MTc0MDk3N30.7nBM4X7b-ausYzFQeRe51rKk0YnZYMjn3SZZGbsKN1S7tV-4UkyvcIK4ABECS_ST4C9-rcU0ObXLLN45Em154g"}
while True:
    if sleep_counter==50:
        time.sleep(60)
        sleep_counter=0
    else:
        sleep_counter+=1
    try:
        #prosess current state
        print(f"iteration={page_iteration}| time={datetime.now()}")
        #url
        url=f"https://api.jagran.com/api/jagran/articlesbystatecity/uttar-pradesh/lucknow-city/{page_iteration}/10"
        #html request
        response_head=requests.get(url,headers=payload)
        #decoding data
        response=response_head.content.decode("utf-8",errors="ignore")
        #searalising data for extraction
        json_dump=json.loads(response)
        #sending data to celery workers for execution
        filter_jagaran_data.delay(json_dump)
        #increasing page number
        page_iteration+=1
    except Exception as e:
        print(e)    
        print(f"""
                Data_log_entry--->\n
            page_iteration:{page_iteration}\n
            current json_dump:{json_dump}
        """)
        exit()
