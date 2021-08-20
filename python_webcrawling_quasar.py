from os import link
import time as time
import pandas as pd
# import getpass
# import urllib.request
# import random
import os
from bs4 import BeautifulSoup
from matplotlib.pyplot import text
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from time import sleep

print("찾으시는 핫딜이 있습니까? 입력해보세요")
need_it = input()   # 찾는 키워드 입력
mydata = []         # 데이터를 저장할 리스트 선언

driver = webdriver.Chrome('C:\\Users\\JH\\Downloads\\chromedriver.exe') # 크롬 드라이버 경로입력

driver.get('https://quasarzone.com/')   # 퀘이사존 홈페이지 오픈
time.sleep(1)                           # 홈페이지 오픈을 위해 1초 대기

def gointo_sel(wow):    # selector 경로 이용
    x = driver.find_element_by_css_selector(wow)
    x.click()
    time.sleep(3)

# def gointo_xpath(wow):  # xpath 경로 이용
#     x = driver.find_element_by_xpath(wow)
#     x.click()
#     time.sleep(3)

# def gointo_name(wow):   # name 경로 이용
#     x = driver.find_element_by_name(wow)
#     x.click()
#     time.sleep(3)

def get_content():
    # x = driver.page_source
    # soup = BeautifulSoup(x, 'lxml')   # BeaurifulSoup 사용세팅
    for infonum in range(1,31):
        # 위에서 부터 30번째 게시글까지만 확인합니다 (한페이지당 게시글 30개까지 나열)

        # info = '''#frmSearch > div > div.list-board-wrap > div.market-type-list.market-info-type-list.relative > table > tbody > tr:nth-child(1) > td:nth-child(2) > div > div.market-info-list-cont > p > a > span'''    
        # 첫번째 게시글의 selector 주소

        info = '''#frmSearch > div > div.list-board-wrap > div.market-type-list.market-info-type-list.relative > table > tbody > tr:nth-child({}) > td:nth-child(2) > div > div.market-info-list-cont > p > a > span'''.format(infonum)    
        # for문의 infonum번째 글의 제목명
        stat = '''#frmSearch > div > div.list-board-wrap > div.market-type-list.market-info-type-list.relative > table > tbody > tr:nth-child({}) > td:nth-child(2) > div > div.market-info-list-cont > p > span'''.format(infonum)
        # for문의 infonum번째 글의 판매상태
        won  = '''#frmSearch > div > div.list-board-wrap > div.market-type-list.market-info-type-list.relative > table > tbody > tr:nth-child({}) > td:nth-child(2) > div > div.market-info-list-cont > div > p:nth-child(1) > span:nth-child(2) > span'''.format(infonum)
        # for문의 infonum번째 글의 가격
        link = '''#frmSearch > div > div.list-board-wrap > div.market-type-list.market-info-type-list.relative > table > tbody > tr:nth-child({}) > td:nth-child(2) > div > div.market-info-list-cont > p > a'''.format(infonum)
        # for문의 infonum번째 글의 진입링크

        infotxt = driver.find_elements_by_css_selector(info)[0].text
        # infotxt = soup.select(info)[0].text   # 위 코드와 동일 기능
        wontxt  = driver.find_elements_by_css_selector(won)[0].text
        # wontxt  = soup.select(won)[0].text    # 위 코드와 동일 기능
        stattxt = driver.find_elements_by_css_selector(stat)[0].text
        # stattxt = soup.select(stat)[0].text   # 위 코드와 동일 기능

        mydata.append([stattxt, infotxt, wontxt])
        
        if need_it in infotxt:
            print('''
        **** 현시각 지름/할인정보 상위 {}번째글 [상태: {}] ****
        {} // {}'''.format(infonum, stattxt, infotxt, wontxt))
            # driver.find_elements_by_css_selector(link)[0].click()
            # break

sale_dir_sel = '#header > div.all-menu-wrap > ul > li:nth-child(7) > div > dl > dd:nth-child(1) > p:nth-child(1) > a'
firsttap_sel = '#header > div.all-menu-wrap > ul > li:nth-child(7) > a'

gointo_sel(firsttap_sel)    # 1차 메뉴 탭 핫딜/장터 클릭
gointo_sel(sale_dir_sel)    # 2차 메뉴 탭 지름/할인정보 클릭

get_content()               # 게시판 내용 크롤링

nextpage_sel = '#frmSearch > div > div.list-util-area > div.paging-box > div > ul > li:nth-child(2) > a'
gointo_sel(nextpage_sel)    # 다음페이지 넘어가기
get_content()               # 게시판 내용 크롤링

mydata = pd.DataFrame(mydata)   # 크롤링 결과들을 데이터프레임으로 정리
# mydata.index = [range(1,31)]  # 인덱스 지정
mydata.columns = [['판매상태', '게시글 제목', '할인가']] # 컬럼명 지정
print('\n\n', mydata)           # 터미널에 한번 띄우기
mydata.to_csv('./지름과할인정보.csv', encoding='euc-kr')    # csv파일로 저장
print('csv파일 저장위치 -', os.getcwd())          # 저장위치 출력

driver.close()              # 브라우저 종료