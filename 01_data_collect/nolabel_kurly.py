import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
import math
import re
import json
from datetime import datetime
import csv


def total_cnt(driver):
    # 전체 페이지 수 구하기.
    # 한 페이지에 나오는 상품의 수 = 12개 (검색상품 기본값)
    # 전체 상품 수 / 12 = 페이지 수 
    target_url = "https://www.kurly.com/search?sword=무라벨"
    driver.get(target_url)
    sleep(3)
    soup = BeautifulSoup(driver.page_source, "lxml")
    sleep(3)
    items_cnt = soup.select_one(".css-1f8etfr.eudxpx34 > div").get_text()
    items_cnt = re.sub(r'[^0-9]', '', items_cnt).strip()
    pages_cnt = int(items_cnt) / 12
    pages_cnt = math.ceil(pages_cnt)
    return items_cnt, pages_cnt



def kurly_crawling(driver, filename):
    items_cnt, pages_cnt = total_cnt(driver)
    print("총 제품 개수 : ", items_cnt)
    print("총 페이지 : ", pages_cnt)
    cnt = 1
    for i in range(1, pages_cnt + 1):
        print("*" * 80)
        print(i, " 페이지 저장 시작")

        # api 요청(get) : 상품 번호 
            # 크롤링시 상품번호 X , 상품별 url X 
            # api에서 [상품번호] 가져와서 "https://www.kurly.com/goods/ + [상품번호]" 으로 url 만들어줘야 함.
            # 201 error : Authorization
            # Authorization 계속 바꿔줘야 함.
        header = {'Authorization':'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjYXJ0X2lkIjoiNzJhMmQ5MmEtYTc4MS00Yzc4LTk0MzUtMWFjOGRhYzkwNjQ5IiwiaXNfZ3Vlc3QiOnRydWUsInV1aWQiOm51bGwsIm1fbm8iOm51bGwsIm1faWQiOm51bGwsImxldmVsIjpudWxsLCJzdWIiOm51bGwsImlzcyI6Imh0dHA6Ly9hcGkua3VybHkuY29tOjgwNDMvdjMvYXV0aC9yZWZyZXNoIiwiaWF0IjoxNjYyNTMzOTQzLCJleHAiOjE2NjI1Mzc2MTIsIm5iZiI6MTY2MjUzNDAxMiwianRpIjoibjFhZ011SXlSbUlvQ2p3TCJ9.0RYepiGbDXtNKMLr0U21RxgkitfoshzVjAlWIDj3doE'}
        url = f"https://api.kurly.com/search/v2/normal-search?keyword=무라벨&sort_type=&page={i}&per_page=12"
        
        # convert json to dict
        items_json = json.loads(requests.get(url, headers=header).text)

        items = items_json["data"]
        page_total_items = []
        for item in items:
            temp = []
            id = str(datetime.now()).replace('-', '').replace(':', '').replace(' ', '').split('.')[0]

            sleep(1)

            title = item["name"]
            category1 = "식품"
            category2 = "음료"
            category3 = None
            price = item["sales_price"]
            date = id[:8]

            no = item["no"]
            link = f"https://www.kurly.com/goods/{no}"

            img = item["list_image_url"]

            temp.append(id)
            temp.append(title)
            temp.append(category1)
            temp.append(category2)
            temp.append(category3)
            temp.append(price)
            temp.append(date)
            temp.append(link)
            temp.append(img)
            page_total_items.append(temp)

            print(f"[{cnt} 번째 무라벨 상품]")
            print(f"title : {title}")
            print(f"img : {img}")
            cnt += 1

        with open(filename, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # writer.writerow(['id', 'title', 'category1', 'category2', 'category3', 'price', 'upload_date', 'link', 'img_link'])
            writer.writerows(page_total_items)
            print(f'{i} 번째 페이지 물품 저장 완료')



if __name__ == '__main__':

    # 저장할 파일 미리 생성
    filename = 'nolabel_kurly.csv'
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'category1', 'category2', 'category3', 'price', 'upload_date', 'link', 'img_link'])

    # driver 생성
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    today = str(datetime.now().date()).replace('-', '')

    # 크롤링 시작
    kurly_crawling(driver, filename)

    # driver 종료
    driver.close()


