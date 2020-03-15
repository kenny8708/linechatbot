from __future__ import unicode_literals
from flask import Flask, request, abort
import os
import sys
import redis
import psycopg2
import datetime

from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, FileMessage, StickerMessage, StickerSendMessage
)
from linebot.utils import PY3

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

HOST = "redis-16496.c114.us-east-1-4.ec2.cloud.redislabs.com"
PWD = "XBD7myH78zcTm17UmsB0tjoMzVsPnmei"
PORT = "16496" 

redis1 = redis.Redis(host = HOST, password = PWD, port = PORT)
redis1.flushdb()

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        #while True:
        #    msg = input("Please enter your query (type 'quit' or 'exit' to end):").strip()
        #    if msg == 'quit' or msg == 'exit':
        #        break
        #    if msg == '':
        #        continue
        #   print("You have entered " + msg, end=' ') 
        #   X = redis1.incr(msg)
        #   print('for',X,'times')         
        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, TextMessage):
            handle_TextMessage(event)
        if isinstance(event.message, ImageMessage):
            handle_ImageMessage(event)
        if isinstance(event.message, VideoMessage):
            handle_VideoMessage(event)
        if isinstance(event.message, FileMessage):
            handle_FileMessage(event)
        if isinstance(event.message, StickerMessage):
            handle_StickerMessage(event)
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

    return 'OK'

# Handler function for Text Message
def handle_TextMessage(event):
    if 'Mask'  in event.message.text:
        try:
         repsonse = line_select_overall(event.message.text)
         line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=repsonse)
         )
        except:
         line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Please retry it later')
         )
    elif 'Clinic' in event.message.text:
        try:
         repsonse = line_select_overall(event.message.text)
         line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=repsonse)
         )
        except:
         line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Please retry it later')
         )
    elif 'Case'  in event.message.text:
        try:
         repsonse = line_select_overall(event.message.text)
         line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=repsonse)
         )
        except:
         line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Please retry it later')
         )
    elif 'Record' in event.message.text:
        try:
         record_list = prepare_record(event.message.text)
         reply = line_insert_record(record_list)
         line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
         )
        except:
         line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Please retry it later')
         )
    else:
           #while True:
        #    msg = input("Please enter your query (type 'quit' or 'exit' to end):").strip()
        #    if msg == 'quit' or msg == 'exit':
        #        break
        #    if msg == '':
        #        continue
        #   print("You have entered " + msg, end=' ') 
        #   X = redis1.incr(msg)
        #   print('for',X,'times')   
         X = redis1.incr(event.message.text)
         msg = 'I don\'t understand ' + event.message.text + ' for 'X' time'
         line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )

def line_select_overall(text):
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    postgres_select_query = f"""SELECT * FROM Response WHERE keyword = %s;"""
    cursor.execute(postgres_select_query,(text,))
    record = cursor.fetchall()

    for row in record:
        print (row[2],)
    cursor.close()
    conn.close()
    return row[2] 
 

def prepare_record(text):
    text_list = text.split('\n')   
    record_list = []
    
    for i in text_list[1:]:
        temp_list = i.split(' ')
        
        temp_name = temp_list[0]
        temp_training = temp_list[1]

        record = (temp_name, temp_training)
        record_list.append(record)
        
    return record_list     
    

# Handler function for Sticker Message
def handle_StickerMessage(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )

# Handler function for Image Message
def handle_ImageMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice image!")
    )

# Handler function for Video Message
def handle_VideoMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice video!")
    )

# Handler function for File Message
def handle_FileMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice file!")
    )

def line_insert_record(record_list):
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    table_columns = '(keyword,response)'
    postgres_insert_query = f"""INSERT INTO Response {table_columns} VALUES (%s,%s)"""
    cursor.executemany(postgres_insert_query, record_list)
    conn.commit()

    message = f"恭喜您！ {cursor.rowcount} 筆資料成功匯入 Response 表單！"
    print(message)

    cursor.close()
    conn.close()
    
    return message

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)
