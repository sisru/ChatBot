import pymongo
import requests
from html2text import html2text
from bs4 import BeautifulSoup
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

conn = pymongo.MongoClient('127.0.0.1')
db = conn.chatbot


def make_list(input_data):
    collect = db.univ
    select_div = input_data[0]
    select_data = input_data[1]

    query = {"$and": [{'div': select_div},
                      {select_data: {"$exists": "true"}}
                      ]
             }
    data = collect.find(query)

    a_list = data[0][select_data]
    next_node = data[0]['next_node']
    return a_list, next_node


def make_keyboard(input_list, next_node):
    keyboard = []
    for data in input_list:
        return_data = str(next_node) + ',' + str(data)
        keyboard.append([InlineKeyboardButton(text=str(data), callback_data=str(return_data))])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return keyboard


def make_reply_string(input_data):
    collect = db.univ
    select_div = input_data[0]
    select_data = input_data[1]

    query = {"$and":
                 [{'div': select_div},
                  {select_data: {"$exists": "true"}}
                  ]
             }
    print(query)
    data = collect.find_one(query)
    info = data[select_data]
    print(info)

    reply_string = "성함 : " + select_data + "\n"
    reply_string += "소속 : " + str(info['prof_major']) + "\n"
    reply_string += "연락처 : " + str(info['prof_tel']) + "\n"
    reply_string += "연구실 : " + str(info['prof_lab']) + "\n"

    return reply_string


def get_weather():
    url = 'http://www.kma.go.kr/wid/queryDFSRSS.jsp?zone=2629061000'
    #   url = 'http://www.kma.go.kr/wid/queryDFS.jsp?gridx=98&gridy=75' 동명대학교 그리드좌표.

    req = requests.get(url)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    return_string = ""
    cat = str(soup.find_all("category")[0])
    cat = html2text(cat).strip()

    wth = str(soup.find_all("wfkor")[0])
    wth = html2text(wth).strip()

    if wth.find("비") >= 0:
        rain = str(soup.find_all("r12")[0])
        rain = html2text(rain).strip()
        return_string += str(cat) + "의 날씨는 " + str(wth) + "이며, 예상강수량은 " + rain + "입니다."

    elif wth.find("눈") >= 0:
        snow = str(soup.find_all("s12")[0])
        snow = html2text(snow).strip()
        return_string += str(cat) + "의 날씨는 " + str(wth) + "이며, 예상적설량은 " + snow + "입니다."

    else:
        return_string += str(cat) + "의 날씨는 " + str(wth) + "입니다."

    return return_string

def select(query_data, chat_id, bot):
    if query_data[0] == '날씨':
        bot.sendMessage(chat_id, get_weather())

    elif query_data[0] == '구독':

        tam = db.sub.find_one({"channel": chat_id})
        print(chat_id)
        print(tam)

        if tam == None:
            sub_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='구독하기', callback_data='신청')],
            ])

        else:
            sub_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='구독해지', callback_data='해지')],
            ])

        bot.sendMessage(chat_id, '선택해주세요.', reply_markup=sub_keyboard)

    elif query_data[0] == '신청':
        db.sub.insert_one({'channel': chat_id})
        bot.sendMessage(chat_id, '구독이 완료되었습니다. :)')

    elif query_data[0] == '해지':
        db.sub.delete_one({'channel': chat_id})
        bot.sendMessage(chat_id, '구독이 해지되었습니다. :(')

    elif query_data[0] == '완료':
        reply_string = make_reply_string(query_data)
        bot.sendMessage(chat_id, reply_string)

    else:
        reply_list, next_node = make_list(query_data)
        reply_keyboard = make_keyboard(reply_list, next_node)
        reply_ment = "원하시는 " + query_data[0] + "를 선택해주세요."
        bot.sendMessage(chat_id, reply_ment, reply_markup=reply_keyboard)