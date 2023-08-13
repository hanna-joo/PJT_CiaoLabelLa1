# 무라벨 상품 중 네이버페이 상품만
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
    # 전체 페이지 수 구하기
    # 한 페이지에 나오는 상품의 수 = 40개 (기본값)
    # 전체 상품 수 / 40 = 페이지 수
    target_url = f"https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery={keyword}&pagingIndex=1&pagingSize=40&productSet=checkout&query={keyword}&sort=date&timestamp=&viewType=list"
    driver.get(target_url)
    soup = BeautifulSoup(driver.page_source, "lxml")
    items_cnt = soup.select_one(".subFilter_seller_filter__snFam > li:nth-child(3) > a > span:nth-child(1)").get_text()
    items_cnt = items_cnt.replace(",", "")
    pages_cnt = int(items_cnt) / 40
    pages_cnt = math.ceil(pages_cnt)
    return pages_cnt, items_cnt

def naver_crawling(driver, keyword, filename):
    pages_cnt, items_cnt = total_cnt(driver, keyword)
    print("총 제품 개수 : ", items_cnt)
    print("총 페이지 : ", pages_cnt)
    sleep(5)
    cnt = 1
    for i in range(1, pages_cnt + 1):
        print("*" * 80)
        print(i, " 페이지 저장 시작")
        # 네이버 페이 상품 페이지 : productSet=checkout
        target_url = f"https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery={keyword}&pagingIndex={i}&pagingSize=40&productSet=checkout&query={keyword}&sort=date&timestamp=&viewType=list"
        driver.get(target_url)
        body = driver.find_element(By.CSS_SELECTOR, 'body')
        #body.click()
        sleep(3)
        for j in range(15):
            body.send_keys(Keys.PAGE_DOWN)
            sleep(0.2)
        soup = BeautifulSoup(driver.page_source, "lxml")

        # 파싱
        items = soup.select(".basicList_item__0T9JD")
        page_total_items = []
        for item in items:
            temp = []
            id = str(datetime.now()).replace('-', '').replace(':', '').replace(' ', '').split('.')[0]
            title = item.select_one(".basicList_info_area__TWvzp > div:nth-child(1)").get_text()
            try:
                category1 = item.select_one(".basicList_depth__SbZWF > span:nth-child(1)").get_text()
            except AttributeError:
                category1 = None
            try:
                category2 = item.select_one(".basicList_depth__SbZWF > span:nth-child(2)").get_text()
            except AttributeError:
                category2 = None
            try:
                category3 = item.select_one(".basicList_depth__SbZWF > span:nth-child(3)").get_text()
            except AttributeError:
                category3 = None
            price = item.select_one(".price_num__S2p_v").get_text()
            etc = item.select_one(".basicList_etc_box__5lkgg ").get_text()
            date = re.search(r"(?<=등록일 ).*?(?=.찜하기)", etc).group(0).replace('.', '')
            link = item.select_one(".basicList_title__VfX3c > a ")["href"]
            # img ::before <- 가상요소
            try:
                img = item.select_one(".thumbnail_thumb_wrap__RbcYO > a > img")["src"]
                # imgs 폴더에 사진 저장
                #urllib.request.urlretrieve(img, f"imgs/{id}.jpg")
            except TypeError :
                img = "no image"
            else:
                img = item.select_one(".thumbnail_thumb__Bxb6Z > img")["src"]
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
        sleep(1)

        with open(filename, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            #writer.writerow(['id', 'title', 'category1', 'category2', 'category3', 'price', 'upload_date', 'link', 'img_link'])
            writer.writerows(page_total_items)
            print(f'{i} 번째 페이지 물품 저장 완료')

        sleep(1)


if __name__ == '__main__':

    # 저장할 파일 미리 생성
    filename = 'nolabel_naver.csv'
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'category1', 'category2', 'category3', 'price', 'upload_date', 'link', 'img_link'])

    # driver 생성
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    #today = str(datetime.now().date()).replace('-', '')

    # 크롤링 시작
    naver_crawling(driver, '무라벨', filename)

    # driver 종료
    driver.close()






