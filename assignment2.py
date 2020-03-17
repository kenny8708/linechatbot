from __future__ import unicode_literals
from flask import Flask, request, abort
import os
import sys
import redis
import psycopg2
import datetime
import subprocess

from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import *
from linebot.utils import PY3

import pandas as pd  
import io  
import requests  


app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

HOST = "redis-16496.c114.us-east-1-4.ec2.cloud.redislabs.com"
PWD =  "XBD7myH78zcTm17UmsB0tjoMzVsPnmei"
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

# Latest COVID-19 Statistics in HK
url1="http://www.chp.gov.hk/files/misc/latest_situation_of_reported_cases_wuhan_eng.csv"  
s=requests.get(url1).content  
hk=pd.read_csv(io.StringIO(s.decode('utf-8')))

hk1=hk.iloc[-1]['As of date']
hk2=hk.iloc[-1]['Number of confirmed cases']
hk3=hk.iloc[-1]['Number of ruled out cases']
hk4=hk.iloc[-1]['Number of cases still hospitalised for investigation']
hk5=hk.iloc[-1]['Number of cases fulfilling the reporting criteria']
hk6=hk.iloc[-1]['Number of death cases']
hk7=hk.iloc[-1]['Number of discharge cases']
hk8=hk.iloc[-1]['Number of probable cases']

                              
# Handler function for Text Message
def handle_TextMessage(event):
#  Text Message (Latest COVID-19 Statistics in HK)
    if event.message.text == "HK Stat": 
        try:   
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'Latest COVID-19 Statistics in HK \nConfirmed: {hk2} \nProbable: {hk3} \nDeath: {hk4} \nDischarged: {hk5} \nHospitalised: {hk6} \nRuled out: {hk7} \nReported: {hk8} \n--------- \nData Source: data.gov.hk \nLast Updated on: {hk1} \nUpdate Frequency: Every Night' 
            )
        )
        except:
         line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text='Please retry it later')
         )
#    elif event.message.text == "Clinic": 
#        line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text=event.message.text)
#        )
#    elif event.message.text == "Case": 
#        line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text=event.message.text)
#        )

# Buttons Template (Latest COVID-19 Statistics in HK)
    if event.message.text == "Case":
        try: 
        buttons_template = TemplateSendMessage(
        alt_text='Please check on smartphone.',
        template=ButtonsTemplate(
            title='Hong Kong',
            text='Please select',
            thumbnail_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Flag_of_Hong_Kong.svg/2560px-Flag_of_Hong_Kong.svg.png',
            actions=[
                MessageAction(
                    label='Latest Statistics',
                    text='HK Stat'
                ),
                URIAction(
                    label='Dashboard',
                    uri='https://chp-dashboard.geodata.gov.hk/covid-19/en.html'
                ),
            ]
        )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        except:
         line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text='Please retry it later')
         )
# Carousel Template (Mask Supply)
    if event.message.text == "Mask": 
        try:
         carousel = TemplateSendMessage(
         alt_text='Please check on smartphone.',
         template=CarouselTemplate(
           columns=[
            CarouselColumn(
                 thumbnail_image_url='https://static.stheadline.com/stheadline/inewsmedia/20200316/_2020031612385066621.jpeg',
                 title='Mask Brand',
                 text='Please select',
                 actions=[
                    MessageAction(
                        label='3M',
                        text='3M Mask'
                    ),
                    MessageAction(
                        label='Medicom',
                        text='Medicom Mask'
                    ),
                    MessageAction(
                        label='超立體',
                        text='超立體口罩'
                    )
                ]
            ),
            CarouselColumn(
                 thumbnail_image_url='https://media.nationthailand.com/images/news/2020/01/27/30381117/800_a4aa7825d86de8e.jpg?v=1580100536',
                 title='Mask location',
                 text='Please select',
                 actions=[
                    URIAction(
                        label='Watson Mask',
                        uri='https://play.google.com/store/apps/details?id=com.ndn.android.watsons&hl=en_US'
                    ),
                    URIAction(
                        label='HKTVmall Online',
                        uri='https://www.hktvmall.com/hktv/en/main/search?q=%3Arelevance%3Astreet%3Amain%3Acategory%3AAA11727500001'
                    ),
                    MessageAction(
                        label='Physical Store',
                        text='Mask Location'
                    )
                ]
            )
        ]
    )
    )
    line_bot_api.reply_message(event.reply_token,carousel)
       except:
         line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text='Please retry it later')
         )
#Location function
    if event.message.text == "Mask Location":
        try:    
        line_bot_api.reply_message(event.reply_token,LocationSendMessage(
            title='Mask location', 
            address='Kai Tin Shopping Centre', 
            latitude=22.308132, 
            longitude=114.237416)
        )
        except:
         line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text='Please retry it later')
         )
    
#elif event.message.text == "Case":
#        buttons_template = TemplateSendMessage(
#        alt_text='Please check on smartphone.',
#        template=ButtonsTemplate(
#            title='Hong Kong',
#            text='Please select',
#            thumbnail_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Flag_of_Hong_Kong.svg/2560px-Flag_of_Hong_Kong.svg.png',
#            actions=[
#                MessageAction(
#                   label='Latest Statistics',
#                   text='HK Stat'
#               ),
#               URIAction(
#                   label='Dashboard',
#                   uri='https://chp-dashboard.geodata.gov.hk/covid-19/en.html'
#               ),
#           ]
#        )
#        )
#        line_bot_api.reply_message(event.reply_token, buttons_template)


# Text Message (count)
    else:
        X = redis1.incr(event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'You said {event.message.text} for {X} time')
        )            


# Handler function for Text Message (Kenny's version)
#     if 'Mask' in event.message.text:
#       try:
#         repsonse = line_select_overall(event.message.text)
#         line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text=repsonse)
#         )
#        except:
#         line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text='Please retry it later')
#         )
#    elif 'Clinic' in event.message.text:
#        try:
#         repsonse = line_select_overall(event.message.text)
#         line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text=repsonse)
#         )
#        except:
#         line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text='Please retry it later')
#         )
#    elif 'Case' in event.message.text:
#        try:
#         repsonse = line_select_overall(event.message.text)
#         line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text=repsonse)
#         )
#        except:
#         line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text='Please retry it later')
#         )
#    elif 'Record' in event.message.text:
#        try:
#         record_list = prepare_record(event.message.text)
#         reply = line_insert_record(record_list)
#         line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text=reply)
#         )
#        except:
#         line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text='Please retry it later')
#         )
#    else:
#         X = redis1.incr(event.message.text)
#         line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text=f'You said {event.message.text} for {X} time')
#        )



        # msg = 'I don\'t understand "' + event.message.text + '"'
        # line_bot_api.reply_message(
        #    event.reply_token,
        #    TextSendMessage(text=msg)
        #)
      
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
	TextSendMessage(text="Nice image! Let's fight the virus together!")
    )

# Handler function for Video Message
def handle_VideoMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice video! Let's fight the virus together!")
    )

# Handler function for File Message
def handle_FileMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice file! Let's fight the virus together!")
    )

def line_insert_record(record_list):
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    table_columns = '(keyword,response)'
    postgres_insert_query = f"""INSERT INTO Response {table_columns} VALUES (%s,%s)"""
    cursor.executemany(postgres_insert_query, record_list)
    conn.commit()

    message = f" {cursor.rowcount} Record addes into Response "
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
