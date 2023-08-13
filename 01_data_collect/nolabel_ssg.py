# SSG 닷컴의 무라벨 상품
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json
from time import sleep
import math
import urllib.request
import re
from datetime import datetime
import csv

def total_cnt(driver, keyword):
    # 특정 키워드 검색 후 신상품 순 제품 조회
    target_url = f"https://www.ssg.com/search.ssg?target=all&query={keyword}&sort=regdt"
    driver.get(target_url)
    soup = BeautifulSoup(driver.page_source, "lxml")
    # 전체 페이지 및 전체 상품 개수
    pages_cnt = int(soup.select_one("#area_searchItemList #item_navi > a.btn_last")["data-filter-value"].split('=')[1])
    items_cnt = int(soup.select_one("#target_item_count")["value"])
    return pages_cnt, items_cnt

def ssg_crawling(driver, keyword, filename):
    cnt = 0
    soldout = 0
    pages_cnt, items_cnt = total_cnt(driver, keyword)
    print("총 제품 개수 : ", items_cnt)
    print("총 페이지 : ", pages_cnt)
    for i in range(pages_cnt):
        target_url = f"https://www.ssg.com/search.ssg?target=all&query={keyword}&sort=regdt&page={i+1}"
        driver.get(target_url)
        sleep(2)
        soup = BeautifulSoup(driver.page_source, "lxml")
        sleep(1)
        # 파싱---------
        # 제품들
        items = soup.select("#area_searchItemList li")
        page_total_items = []
        for item in items:
            temp = []
            if item.select_one("div.cunit_soldout"):
                soldout += 1
                continue
            else:
                cnt += 1
                id = str(int(str(datetime.now()).replace('-', '').replace(':', '').replace(' ', '').split('.')[0]) + cnt)
                title = item.select_one("div.cunit_info div.title > a > em.tx_ko").text
                price = item.select_one("div.cunit_info div.cunit_price em.ssg_price").get_text().replace(',', '')
                link = 'https://www.ssg.com' + item.select_one(".cunit_t232 div.thmb > a")['href']
                img = 'https:' + item.select_one(".cunit_t232 div.thmb > a > img:nth-child(1)")['src']
                temp.append(id)
                temp.append(title)
                temp.append(price)
                temp.append(link)
                temp.append(img)
                page_total_items.append(temp)
                # 저장 row 확인
                print(f"[무라벨 {cnt}개, 품절 {soldout}개, 총 {cnt + soldout}개 / {item_cnt}개]")
                print(f"title : {title}")
                print(f"img : {img}")

        with open(filename, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(page_total_items)
            print(f'{i+1} 번째 페이지 물품 저장 완료')

    print(cnt)



if __name__ == '__main__':

    # 저장할 파일 미리 생성
    filename = 'nolabel_ssg.csv'
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'price', 'link', 'img_link'])

    # driver 생성
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # 크롤링 시작
    ssg_crawling(driver, '무라벨', filename)

    # driver 종료
    driver.close()






