# pip install (selenium, BeautifulSoup4, pandas, requests, wordcloud, tqdm, folium, seaborn, openpyxl)

import time
import re # 인스타그램 게시글 정보 가져오기
import unicodedata # 인스타그램 게시글 정보 가져오기
import pandas as pd # 크롤링 결과 저장하기
import requests # 카카오 검색 API 사용
import folium # 지도 표시하기
import matplotlib.pyplot as plt # 시각화 라이브러리 호출 및 환경 설정(한글 폰트)
import seaborn as sns # 시각화 라이브러리 호출 및 환경 설정(한글 폰트)
import sys # 시각화 라이브러리 호출 및 환경 설정(한글 폰트)
import platform # 워드클라우드 라이브러리 불러오기
from matplotlib import font_manager, rc # 시각화 라이브러리 호출 및 환경 설정(한글 폰트)
from collections import Counter # 빈도수 집계하기(Counter)
from bs4 import BeautifulSoup # # 인스타그램 게시글 정보 가져오기 (html을 python이 이해하는 객체 구조로 변환)
from selenium import webdriver # 크롬 브라우저 열기 -> URL 접속
from tqdm.notebook import tqdm # 반복작업 진행시 진행바 표시하기위한 라이브러리 tqdm 활용하기
from folium.plugins import MarkerCluster #지도 표시하기(마커 집합)
from wordcloud import WordCloud

# 크롬 브라우저 열기 -> 인스타그램 접속
driver=webdriver.Chrome('C:\\Users\\JH\\Downloads\\/chromedriver.exe')
driver.get('https://www.instagram.com')
time.sleep(3)

# 인스타그램 로그인을 위한 계정 정보
email='인스타그램 아이디'
input_id = driver.find_elements_by_css_selector('input._2hvTZ.pexuQ.zyHYP')[0]
input_id.clear()
input_id.send_keys(email)

password='인스타그램 비밀번호'
input_pw = driver.find_elements_by_css_selector('input._2hvTZ.pexuQ.zyHYP')[1]
input_pw.clear()
input_pw.send_keys(password)
input_pw.submit()
time.sleep(5)

# 해당 키워드 검색 결과 페이지의 url을 생성 -> 반환하는 함수 정의
def insta_searching(word):
    url ="https://www.instagram.com/explore/tags/" + str(word)
    return url

# 검색결과 페이지 접속하기
word = "강남역맛집"
url = insta_searching(word)
driver.get(url)
time.sleep(10)

# 검색 결과 페이지에서 첫 번째 게시물을 클릭하는 함수 정의
"""
def select_first(driver):
    first=driver.find_elements_by_css_selector("div._9AhH0")
    print(first)
    first.click()
    time.sleep(3)

select_first(driver)
"""

#페이지가 완전히 로드된 후 첫번째 게시물을 클릭해야하기때문에 time.sleep 시간을 충분히 주어야 함
first=driver.find_elements_by_css_selector("div._9AhH0")[0]

first.click()
time.sleep(3)

# 본문 내용, 작성일자, 좋아요 수, 위치 정보, 해시태그를 가져오는 함수
def get_content(driver):
    # ① 현재 페이지 html 정보 가져오기
    html = driver.page_source #html 정보 모두 가져오기
    soup = BeautifulSoup(html, 'html.parser') # python 내장 html.parser 이용
    # ② 본문 내용 가져오기
    try:
        # <div>태그와 <span>태그의 차이점 : <span>은 줄 바꿈이 되지 않는다
        content = soup.select('div.C4VMK > span')[0].text
        # 유니코드 문자열 unistr에 대한 정규화 형식 form 반환
        # NFC : 먼저 정준 분해를 적용한 다음, 미리 결합한 문자로 다시 조합
        # macOS에서 작성된 경우 자음/모음이 분리되는 현상이 있어서
        # unicodedata.normalize(form, unistr)
        content = unicodedata.normalize('NFC', content) 
    except:
        content = ' '
    # ③ 본문 내용에서 해시태그 가져오기(정규식 활용)
    # re.findall(pattern, string, flags=0)
    # string에서 겹치지 않는 pattern의 모든 일치를 문자열 리스트로 반환
    # '#'으로 시작하고 '#'뒤에 연속된 문자를 모두 찾아서 리스트 형대로 저장
    tags = re.findall(r'#[^\s#,\\]+', content)
    # ④ 작성일자 정보 가져오기
    date = soup.select('time._1o9PC.Nzb55')[0]['datetime'][:10]
    # ⑤ 좋아요 수 가져오기
    try:
        like = soup.select('div.Nm9Fw > button')[0].text[4:-1]   
    except:
        like = 0
    # ⑥ 위치정보 가져오기
    try: 
        place = soup.select('div.M30cS')[0].text
        place = unicodedata.normalize('NFC', place)
    except:
        place = ''
    # ⑦ 수집한 정보 저장하기
    data = [content, date, like, place, tags]
    return data

get_content(driver)

# 다음 게시글 열고, 다음 게시물로 넘어가는 함수
def move_next(driver):
    # <a>태그는 하이퍼링크를 걸어주는 태그
    right = driver.find_element_by_css_selector ('a.coreSpriteRightPaginationArrow')
    right.click()
    time.sleep(3)

move_next(driver)

# 비어있는 변수(results)만들기
results = [ ]

# 여러 게시물 수집하기
target = 50      # 크롤링할 게시글 수
for i in range(target):
    # 게시글 수집에 오류 발생시 (네트워크 문제, 로그인 등의 이유로)  2초 대기 후, 다음 게시글로 넘어가도록 try, except 구문 활용
    try:
        # get_content의 return값 : data = [content, date, like, place, tags]
        data = get_content(driver)    # 게시글 정보 가져오기
        results.append(data)
        move_next(driver) # 다음 게시글로 이동
    except:
        time.sleep(2)
        move_next(driver)
    
print(results[:2])

# 크롤링 결과 저장하기
results_df = pd.DataFrame(results)
results_df.columns = ['content','data','like','place','tags']
results_df.to_excel('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\jejudo_matzip.xlsx')

# 크롤링 결과 중 해시태그 데이터 불러오기
raw_total = pd.read_excel('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\jejudo_matzip.xlsx')
raw_total['tags'] [:3]

# 크롤링 데이터 불러오기
raw_total.head()

# 해시태그 통합 저장하기
tags_total = []

for tags in raw_total['tags']:
    tags_list = tags[2:-2].split("', '")
    for tag in tags_list:
        tags_total.append(tag)

# 리스트 내에 동일자료가 몇개인지 확인하고 그 값을 저장
tag_counts = Counter(tags_total)

# 가장 많이 사용된 해시태그 살펴보기(50개 찾기)
tag_counts.most_common(50)

# 찾으려는 제주도맛집과 관련이 먼 해시태그 리스트
STOPWORDS = ['#일상', '#선팔', '#좋아요', '#좋아요반사', '#제주도맛집', '#다이어트',
'#네일아트', '#데일리', '#소통', '#맞팔']

tag_total_selected = []
for tag in tags_total:
    if tag not in STOPWORDS:            # 전체 해시태그 중에서 관련없는 해시태그들을 제외하고
        tag_total_selected.append(tag)  # 걸리지 않는 해시태그들을 따로 모음
        
tag_counts_selected = Counter(tag_total_selected)   # 빈도수 확인하고
tag_counts_selected.most_common(50)                 # 최고빈도 50개 추려내기

# 시각화 라이브러리 호출 및 환경 설정(한글 폰트)
if sys.platform in ["win32", "win64"]:
    font_name = "malgun gothic"
elif sys.platform == "darwin":
    font_name = "AppleGothic"

# 막대차트 사용을 위한 세팅(import, 서체 설정)
rc('font',family=font_name)

# 데이터 준비하기
tag_counts_df = pd.DataFrame(tag_counts_selected.most_common(30))   # 선별된 태그중 빈도수 상위30개로 데이터프레임 작성
tag_counts_df.columns = ['tags', 'counts']                          # 컬럼명 지정

# 막대 차트 그리기
plt.figure(figsize=(10,8))                                  # 차트 이미지 크기 조정
sns.barplot(x='counts', y='tags', data = tag_counts_df)     # 막대차트 생성함수, x값과 y값, 내용 데이터

if platform.system() == 'Windows':   #윈도우의 경우
    font_path = "c:/Windows/Fonts/malgun.ttf"
elif platform.system() == "Darwin":   #Mac 의 경우
    font_path = "/Users/$USER/Library/Fonts/AppleGothic.ttf"

# 워드클라우드 만들기
wordcloud=WordCloud(font_path= font_path,       # 글꼴 경로
                    background_color="white",   # 배경색
                    max_words=100,              # 최대표현 단어개수
                    relative_scaling= 0.3,      # 워드클라우드내 상대적크기 설정(0~1)
                width = 800,                    # 가로 길이
                    height = 400                # 세로 길이
                 ).generate_from_frequencies(tag_counts_selected)  
plt.figure(figsize=(15,10))
plt.imshow(wordcloud)
plt.axis('off')                                 # 워드클라우드 생성은 실행마다 무작위로 만들어지기  
plt.savefig('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\2_tag-wordcloud.png')      # 때문에 여러번 실행시켜 적합한 결과물을 찾는것이 좋다

# 위치정보 가져오기
location_counts = raw_total['place'].value_counts( )
location_counts

# 등록된 위치정보별 빈도수 데이터
location_counts_df = pd.DataFrame(location_counts)
location_counts_df.head()
# 위치정보 빈도수 데이터 저장하기
location_counts_df.to_excel('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\jejudo_location.xlsx', index=True)

# 위치정보 종류 확인하기
locations = list( location_counts.index )

# 카카오 로컬 API를 활용한 장소 검색 함수 만들기
def find_places(searching):
    # ① 접속URL 만들기
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(searching)
    # ② headers 입력하기 : 카카오 디벨로퍼 사이트에서 승인받은 어플의 API를 이용해 정보 입력
    headers = {
    "Authorization": "KakaoAK ***************"
    }
    # ③ API 요청&정보 받기 : 결과를 .json 형태로 읽고, 장소 검색 결과가 저장된 'documents' 항목 값 선택
    places = requests.get(url, headers = headers).json()['documents']
    # ④ 필요한 정보 선택하기
    place = places[0] # 정확도가 높은 순서대로 저장되어 첫 번째 결과를 선택
    name = place['place_name']
    x=place['x'] # x좌표
    y=place['y'] # y좌표
    data = [name, x, y, searching] 

    return data

# def getKakaoMapHtml(address_latlng):  # 카카오맵 자체를 이용하는 내용
#     javascript_key = "5eb578345032125053acb58dd3a903bb"
 
#     result = ""
#     result = result + "<div id='map' style='width:300px;height:200px;display:inline-block;'></div>" + "\n"
#     result = result + "<script type='text/javascript' src='//dapi.kakao.com/v2/maps/sdk.js?appkey=" + javascript_key + "'></script>" + "\n"
#     result = result + "<script>" + "\n"
#     result = result + "    var container = document.getElementById('map'); " + "\n"
#     result = result + "    var options = {" + "\n"
#     result = result + "           center: new kakao.maps.LatLng(" + address_latlng[0] + ", " + address_latlng[1] + ")," + "\n"
#     result = result + "           level: 3" + "\n"
#     result = result + "    }; " + "\n"
#     result = result + "    var map = new kakao.maps.Map(container, options); " + "\n"
    
#     # 검색한 좌표의 마커 생성을 위해 추가
#     result = result + "    var markerPosition  = new kakao.maps.LatLng(" + address_latlng[0] + ", " + address_latlng[1] + ");  " + "\n"
#     result = result + "    var marker = new kakao.maps.Marker({position: markerPosition}); " + "\n"
#     result = result + "    marker.setMap(map); " + "\n"
 
#     result = result + "</script>" + "\n"
    
#     return result



# 인스타그램 위치명 위치정보 검색하기
locations_inform = [ ]
for location in tqdm(locations): 
    try: # 위치 정보가 지도에서 검색되지 않는 곳일 경우 에러가 발생하는 것을 방지
        data = find_places(location) 
        print("-----------------------")  
        print(data)    
        print("-----------------------")
        locations_inform.append(data) 
        time.sleep(0.5)
    except:
        pass

# 위치정보 저장하기
locations_inform_df = pd.DataFrame(locations_inform)
locations_inform_df.columns = ['name_official','경도','위도','인스타위치명']
locations_inform_df.to_excel('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\3_locations.xlsx', index=False)

# 인스타 게시량 및 위치정보 데이터 불러오기
location_counts_df = pd.read_excel('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\jejudo_location.xlsx', index_col = 0) # 첫 번째 칼럼을 인덱스로 사용 , index_col = 0
#location_counts_df.columns=['name_official','place'] 
locations_inform_df = pd.read_excel('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\3_locations.xlsx')

# 위치 데이터 병합하기
location_data = pd.merge(locations_inform_df, location_counts_df, # pd.merge : 데이터 병합, 
                         how = 'inner', left_on = 'name_official', right_index=True)

location_data.head()

# 데이터 중복 점검하기
location_data['name_official'].value_counts()

# 장소 이름 기준 병합하기
location_data = location_data.pivot_table(index = ['name_official','경도','위도'], values = 'place', aggfunc='sum')
location_data.head()

# 병합한 데이터 저장하기
location_data.to_excel('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\3_location_inform.xlsx')


## folium 라이브러리를 이용해 지도에 표시##
# 데이터 불러오기
location_data = pd.read_excel('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\3_location_inform.xlsx')
location_data.info()

# 지도 표시하기 -> 지도를 시각화하기 위해 지도의 중심 위치 좌표와 위치별 위도/경도가 필요함
Mt_Hanla =[37.49790901225695, 127.0276449838695] # 강남역을 지도의 중심이라고 지정
map_jeju = folium.Map(location = Mt_Hanla, zoom_start = 20) # 지도 생성

for i in range(len(location_data)):
    name = location_data ['name_official'][i]    # 공식명칭
    count = location_data ['place'][i]           # 게시글 개수
    size = int(count)*2
    long = float(location_data['위도'][i])      
    lat = float(location_data['경도'][i])
    # 원을 생성하는 함수 <.CircleMarker>
    folium.CircleMarker((long,lat), radius = size, color='red', popup=name).add_to(map_jeju) # 각각의 정보를 저장해 지도에 원을 추가함

# 지도를 시각화한 결과물을 html파일로 저장
map_jeju.save('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\3_jeju.html')

# 지도 표시하기(서클 마커) -> 분포를 한눈에 볼 수 있음
locations = []
names = []

for i in range(len(location_data)):
    data = location_data.iloc[i]  # 행 하나씩
    locations.append((float(data['위도']),float(data['경도'])))    # 위도 , 경도 순으로
    names.append(data['name_official'])

map_jeju2 = folium.Map(location = Mt_Hanla, zoom_start = 20)
                       
marker_cluster = MarkerCluster(
    locations=locations, popups=names,
    name='Jeju',
    overlay=True,
    control=True,
)

marker_cluster.add_to(map_jeju2)
folium.LayerControl().add_to(map_jeju2)

# 마커한 지도 저장하기
map_jeju2.save('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\3_jeju_cluster.html')

# 예제 5-44 크롤링 데이터 불러오기
raw_total = pd.read_excel('C:\\Users\\JH\\Desktop\\JH\\새 폴더\\jejudo_matzip.xlsx')
raw_total.head()

"""### 5.4.3 단어 선택하기"""

# 예제 5-45 추출 단어 포함하는 데이터 선택하기
select_word = '먹스타그램'

check_list = []
#'해돋이'글이 포함되어있다면 true, 없다면 false를 저장(check_list에)
for content in raw_total['content']:
    if select_word in content:
        check_list.append(True)
    else:
        check_list.append(False)
        
select_df = raw_total[check_list]
select_df.head()

# 예제 5-46 선택 데이터 확인하기
#'해돋이' 글이 포함되어있는 데이터만 출력
for i in select_df.index:
    #pandas 데이터 레이블로 선택하기
    #i번째 행의 'content'열 내용
    print(select_df.loc[i, 'content']) 
    print('-'*50)

# 예제 5-47 선택 데이터 저장하기
fpath = f'C:\\Users\\JH\\Desktop\\JH\\새 폴더\\4_select_data_{select_word}.xlsx'
select_df.to_excel(fpath)

# 예제 5-48 여러개의 단어 선택/추출/저장하기
select_word_list = ['먹스타그램','강남역맛집','강남맛집','수제버거','초밥']

for select_word in select_word_list:
    check_list = []
    for content in raw_total['content']:
        if select_word in content:
            check_list.append(True)
        else:
            check_list.append(False)

    select_df = raw_total[check_list]
    fpath = f'C:\\Users\\JH\\Desktop\\JH\\새 폴더\\4_select_data_{select_word}.xlsx'
    select_df.to_excel(fpath)