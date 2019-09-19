import time
import telepot
import etc
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='교수정보', callback_data='대학,list')],
        [InlineKeyboardButton(text='날씨정보', callback_data='날씨')],
        [InlineKeyboardButton(text='공지사항 구독', callback_data='구독')],
    ])

    bot.sendMessage(chat_id, '원하시는 기능을 선택해주세요.', reply_markup=keyboard)


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)

    bot.answerCallbackQuery(query_id, text='선택 완료 ! >_<')

    print(query_data)

    chat_id = msg['message']['chat']['id']

    query_data = query_data.split(',')
    etc.select(query_data, chat_id, bot)




TOKEN = "867060334:AAEmENM3qTdhJ0lO9-4Sf3Vz-kiO801ZUX4"

bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)