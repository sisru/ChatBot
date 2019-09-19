import telepot
from bs4 import BeautifulSoup
from selenium import webdriver
import requests, time, pymongo


def chat_id_sum() :
    collect = db.sub
    chat_id_list = []
    docs = collect.find()
    for doc in docs:
        print(doc)
        tmp = doc['channel']
        chat_id_list.append(tmp)

    print(chat_id_list)

    return chat_id_list

#mongoDB 연결
client = pymongo.MongoClient("localhost", 27017)
db = client.get_database('chatbot')

TOKEN = "867060334:AAEmENM3qTdhJ0lO9-4Sf3Vz-kiO801ZUX4"
bot = telepot.Bot(TOKEN)

# tu_crawling > notice
#db = client.get_database('chatbot')
collection = db.get_collection('notice')

path = "chromedriver.exe"
url = "http://www.tu.ac.kr/default3/sub/subLocation.tu?categorySeq=1000005&menuSeq=100000551&confSeq=&boardSeq=-1"

driver = webdriver.Chrome(path)
driver.get(url)

driver.switch_to.frame("iFrameModule")

for i in range(1,2):
    if i != 1:
        link = driver.find_element_by_link_text(str(i))
        link.click()

    time.sleep(1)
    raw_html = str(driver.page_source)
    soup_obj = BeautifulSoup(raw_html, "html.parser")

    stop = 0

    td_list = soup_obj.select("#boardNormalList_ListBoardListVo > tr > td.board_title_font_color > a")
    for tr in td_list:
        notice_href = tr.get('href').replace("#", "")
        notice_title = tr.text
        check_notice = collection.find_one({"href" : notice_href, "title" : notice_title})

        # DB에 존재하지 않는 글일경우. 새 글로 판단. 구독자에게 메세지 발송.
        if check_notice == None:
            collection.insert_one({"href" : notice_href, "title" : notice_title})

            link = "http://www.tu.ac.kr/default/sub/subLocation.tu?categorySeq=1000005&menuSeq=100000551&confSeq=100000185&boardSeq="

            reply_string = "새로운 공지사항입니다.\n"
            reply_string += "제목 : " + str(notice_title) + "\n"
            reply_string += "URL : " + str(link + str(notice_href))

            for i in chat_id_sum() :
                bot.sendMessage(i,reply_string)
        else :
            stop = 1
            break
    if stop == 1 :
        break