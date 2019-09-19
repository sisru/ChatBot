from bs4 import BeautifulSoup
from selenium import webdriver
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import requests, time, pymongo
TOKEN = "844266108:AAHHC8HxOFP0wR73V2LKs7tnG2AGRHw5MXc"
bot = telepot.Bot(TOKEN)
#mongoDB 연결
client = pymongo.MongoClient("localhost", 27017)

# tu_crawling > notice
db = client.get_database('chatbot')
collection = db.get_collection('notice')

path = "chromedriver.exe"
url = "http://www.tu.ac.kr/default3/sub/subLocation.tu?categorySeq=1000005&menuSeq=100000551&confSeq=&boardSeq=-1"

driver = webdriver.Chrome(path)
driver.get(url)

driver.switch_to.frame("iFrameModule")

for i in range(1,11):
    if i != 1:
        link = driver.find_element_by_link_text(str(i))
        link.click()

    time.sleep(1)
    raw_html = str(driver.page_source)
    soup_obj = BeautifulSoup(raw_html, "html.parser")

    td_list = soup_obj.select("#boardNormalList_ListBoardListVo > tr > td.board_title_font_color > a")
    for tr in td_list:
        notice_href = tr.get('href')
        notice_title = tr.text
        check_notice = collection.find_one({"href" : notice_href, "title" : notice_title})

        if check_notice == None:
            collection.insert({"href" : notice_href, "title" : notice_title})

            bot.sendMessage(724541461, "테스트여 ~")
            print("new notice")
        else :
            stop = 1
            break
    if stop == 1 :
        break