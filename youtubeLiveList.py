import pymysql.cursors
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# Chrome 브라우저의 바이너리 경로 지정
chrome_options = Options()
chrome_options.binary_location = '/usr/bin/google-chrome-stable'  # Chrome 바이너리 경로를 확인하고 적절히 수정해주세요.

# ChromeDriver 객체 생성
driver = webdriver.Chrome(options=chrome_options)


def get_channel_live_videos(channel_id):
    # ChromeDriver 실행 및 유투브 화면 불러오기
    # driver = webdriver.Chrome()
    url = f"https://www.youtube.com/{channel_id}/streams"
    driver.get(url)

    # 페이지 로딩을 위한 시간 대기
    time.sleep(3)
    body = driver.find_element("tag name", 'body')
    for i in range(1,31):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)

    # 웹 페이지의 HTML 소스 코드 가져오기
    html = driver.page_source

    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(html, 'html.parser')

    # 작업 완료 후 드라이버 종료
    driver.quit()

    # 영상 목록 가져오기
    videos = []
    for link in soup.find_all("a", {"class": "yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media"}):
        video = {
            "title": link['title'],
            "url": f"https://www.youtube.com{link['href']}"
        }
        videos.append(video)
        print(video['title'])

    return videos

# MySQL 연결 설정
connection = pymysql.connect(
    host='127.0.0.1',
    port=3307,
    user='root',
    password='root1234',
    db='val',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    # 크롤링할 유튜브 채널 ID 입력
    channel_id = "@VCTkr"
    videos = get_channel_live_videos(channel_id)

    with connection.cursor() as cursor:
        # 테이블 생성 (한 번만 실행)
        create_table_query = """
        CREATE TABLE IF NOT EXISTS `live_videos` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `title` VARCHAR(255) NOT NULL,
            `url` VARCHAR(255) NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_table_query)
        connection.commit()

        # 영상 목록을 MySQL에 저장
        for video in videos:
            insert_query = """
            INSERT INTO `live_videos` (`title`, `url`) VALUES (%s, %s)
            """
            cursor.execute(insert_query, (video['title'], video['url']))
            connection.commit()

finally:
    connection.close()