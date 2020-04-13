from __future__ import unicode_literals
from flask import Flask, request, abort
from googletrans import Translator
import os
import sys
import redis
import psycopg2
import datetime
import subprocess
translator = Translator()
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
url1="http://www.chp.gov.hk/files/misc/latest_situation_of_reported_cases_covid_19_eng.csv"  
s=requests.get(url1).content  
hk=pd.read_csv(io.StringIO(s.decode('utf-8')))

hk1=hk.iloc[-1]['As of date']
hk2=hk.iloc[-1]['Number of confirmed cases']
hk3=hk.iloc[-1]['Number of death cases']
hk4=hk.iloc[-1]['Number of discharge cases']
hk5=hk.iloc[-1]['Number of probable cases']
hk6=hk.iloc[-1]['Number of hospitalised cases in critical condition']
hk7=hk.iloc[-1]['As of time']
hk8=hk2+hk5-hk3-hk4

                              
# Handler function for Text Message
def handle_TextMessage(event):
#  Text Message (Latest COVID-19 Statistics in HK)
    if event.message.text == "HK Stat": 
        try:   
         line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=f'Latest COVID-19 Statistics in HK \n\nConfirmed: {hk2} \nProbable: {hk5} \nDeath: {hk3} \nDischarged: {hk4} \nHospitalised: {hk8} \n--------- \nData Source: data.gov.hk \nLast Update: {hk1} {hk7} \nUpdate Frequency: Every Night' 
            )
        )
        except:
         line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text='Please retry it later')
         )

#  Text Message (Case Details)
    if event.message.text.split(' ')[0] == "Case" and (len(event.message.text.split(' ')) == 2):
        cid=event.message.text.split(' ')[1]
        url2="http://www.chp.gov.hk/files/misc/enhanced_sur_covid_19_eng.csv"  
        url3="http://www.chp.gov.hk/files/misc/building_list_eng.csv" 
        s2=requests.get(url2).content
        s3=requests.get(url3).content 
        cc=pd.read_csv(io.StringIO(s2.decode('utf-8')))
        blist=pd.read_csv(io.StringIO(s3.decode('utf-8')))     
        cc_number=cc.loc[cc['Case no.'] == int(cid)]
        cc_number0=cc_number.iloc[0]['Case no.']
        cc_number1=cc_number.iloc[0]['Report date']
        cc_number2=cc_number.iloc[0]['Date of onset']
        cc_number3=cc_number.iloc[0]['Gender']
        cc_number4=cc_number.iloc[0]['Age']
        cc_number5=cc_number.iloc[0]['Name of hospital admitted']
        cc_number6=cc_number.iloc[0]['Hospitalised/Discharged/Deceased']
        cc_number7=cc_number.iloc[0]['HK/Non-HK resident']
        cc_number8=cc_number.iloc[0]['Case classification*']
        cc_number9=cc_number.iloc[0]['Confirmed/probable']
        blist_name=blist.loc[blist['Related probable/confirmed cases'] == cid]
        blist_name1=blist_name.iloc[0]['District']
        blist_name2=blist_name.iloc[0]['Building name']        
        try:   
         line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=f'Case {cc_number0} {cc_number6} \n\n{cc_number7} \nGender: {cc_number3} \nAge: {cc_number4} \n{cc_number8} \n{cc_number1} {cc_number9} \n{cc_number2} Onset \n\nHospital admitted:\n{cc_number5} \n\nBuildings in which cases have resided:\n{blist_name2} \n{blist_name1}'
            )
        )
        except:
         line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text='Please retry it later')
         )


# Carousel Template (Case)
    if translator.translate(event.message.text).text == "Case": 
        try:
         carousel = TemplateSendMessage(
         alt_text='Case Information',
         template=CarouselTemplate(
           columns=[
            CarouselColumn(
                 thumbnail_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Flag_of_Hong_Kong.svg/2560px-Flag_of_Hong_Kong.svg.png',
                 title='Hong Kong COVID-19 Information',
                 text='Please select',
                 actions=[
                    MessageAction(
                        label='Latest Statistics',
                        text='HK Stat'
                    ),
                    URIAction(
                        label='List of Buildings',
                        uri='https://www.chp.gov.hk/files/pdf/building_list_eng.pdf'
                    ),
                    URIAction(
                        label='Quarantine Centres',
                        uri='https://www.chp.gov.hk/files/pdf/quarantine_centre_en.pdf'
                    )
                ]
            ),
            CarouselColumn(
                 thumbnail_image_url='https://raw.githubusercontent.com/kenny8708/linechatbot/master/image/Wordwide_Flag.jpg',
                 title='Worldwide COVID-19 Dashboard',
                 text='Please select',
                 actions=[
                    URIAction(
                        label='HK CHP',
                        uri='https://chp-dashboard.geodata.gov.hk/covid-19/en.html'
                    ),
                    URIAction(
                        label='China CDC',
                        uri='http://2019ncov.chinacdc.cn/2019-nCoV/'
                    ),
                    URIAction(
                        label='WHO',
                        uri='https://who.sprinklr.com/'
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
         
# Carousel Template (Mask Supply)
    if translator.translate(event.message.text).text == "Masks": 
        try:
         carousel = TemplateSendMessage(
         alt_text='Mask Information',
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
                 title='Mask location And Wear Procedure',
                 text='Please select',
                 actions=[
                    URIAction(
                        label='HKTVmall Online',
                        uri='https://www.hktvmall.com/hktv/en/main/search?q=%3Arelevance%3Astreet%3Amain%3Acategory%3AAA11727500001'
                    ),
                    MessageAction(
                        label='Physical Store',
                        text='Mask Location'
                    ),
                    MessageAction(
                        label='How to wear mask',
                        text='Mask Video'
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

# Carousel Template (Clinic)
    if translator.translate(event.message.text).text == "Clinic": 
        try:
         carousel = TemplateSendMessage(
         alt_text='Clinic Information',
         template=CarouselTemplate(
           columns=[
            CarouselColumn(
                 thumbnail_image_url='https://www.ha.org.hk/haho/ho/snp/v3/images/gopc_intro1.jpg',
                 title='All General Out Patient Clinics',
                 text='Please select',
                 actions=[
                    URIAction(
                        label='Hong Kong Island',
                        uri='https://www.ha.org.hk/visitor/ha_isf_result.asp?lang=ENG&service_code_id=461&hospital_type=&service_type=GOPD&location=HK'
                    ),
                    URIAction(
                        label='Kowloon',
                        uri='https://www.ha.org.hk/visitor/ha_isf_result.asp?lang=ENG&service_code_id=461&hospital_type=&service_type=GOPD&location=KLN'
                    ),
                    URIAction(
                        label='New Territories',
                        uri='https://www.ha.org.hk/visitor/ha_isf_result.asp?lang=ENG&service_code_id=461&hospital_type=&service_type=GOPD&location=NT'
                    )
                ]
            ),
            CarouselColumn(
                 thumbnail_image_url='https://www.ha.org.hk/haho/ho/snp/v3/images/gopc_intro2.jpg',
                 title='Special Service Arrangement',
                 text='Please select',
                 actions=[
                    URIAction(
                        label='Non-office Hours',
                        uri='https://www.ha.org.hk/haho/ho/hesd/Public_Holiday_2020_eng_txt.pdf'
                    ),
                    URIAction(
                        label='Re-arrangement',
                        uri='https://www.ha.org.hk/haho/ho/cc-Wuhan/GOPC_service_arrangement_for_appointment_change_and_medication_refill_en_text.pdf'
                    ),
                    URIAction(
                        label='Extreme Weather',
                        uri='https://www.ha.org.hk/visitor/ha_visitor_index.asp?Content_ID=216317&Lang=ENG&Dimension=100&Parent_ID=10052&Ver=HTML'
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
    if translator.translate(event.message.text).text == "Mask Location":
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
    
    if translator.translate(event.message.text).text == "Mask Video":
        try:    
         line_bot_api.reply_message(event.reply_token,VideoSendMessage(
             original_content_url='https://www.youtube.com/watch?v=M4olt47pr_o&feature=youtu.be', 
             preview_image_url='https://www.who.int/images/default-source/health-topics/coronavirus/masks/masks-1.tmb-1920v.png?sfvrsn=38becf2f_3')
             )
        except:
         line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text='Please retry it later')
         )
    if 'Comment' in event.message.text:
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

    if translator.translate(event.message.text).text == "About Us":
        try:    
         Image_Carousel = TemplateSendMessage(
            alt_text='目錄 template',
            template=ImageCarouselTemplate(
            columns=[
            ImageCarouselColumn(
                image_url='https://image.freepik.com/free-vector/business-background-design_1133-247.jpg',
                action=PostbackTemplateAction(
                    label='Comment',
                    text='postback text1',
                    data='action=buy&itemid=1'
                )
            ),
            ImageCarouselColumn(
                image_url='https://image.freepik.com/free-vector/young-man-doubting_1133-526.jpg',
                action=PostbackTemplateAction(
                    label='postback2',
                    text='postback text2',
                    data='action=buy&itemid=2'
                )
            )
        ]
    )
    )     
         line_bot_api.reply_message(event.reply_token,Image_Carousel)
        except:
         line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text='Please retry it later')
         )
         
# Text Message (count)
    elif translator.translate(event.message.text).text == "admincomment": 
            repsonse = line_select_overall(event.message.text)
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'{repsonse}')
        )
    else:          
        X = redis1.incr((event.message.text))
        Y = translator.translate(event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'You said {event.message.text} Translation: {Y.text} for {X} time.')
        )            


def line_select_overall(text):
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    postgres_select_query = f"""SELECT * FROM Response;"""
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
        temp_record = temp_list[1]

        record = (temp_name, temp_record)
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
	TextSendMessage(text="Nice image! \nLet's fight the virus together!")
    )

# Handler function for Video Message
def handle_VideoMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice video! \nLet's fight the virus together!")
    )

# Handler function for File Message
def handle_FileMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice file! \nLet's fight the virus together!")
    )

def line_insert_record(record_list):
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    table_columns = '(keyword,response)'
    postgres_insert_query = f"""INSERT INTO Response {table_columns} VALUES (%s,%s)"""
    cursor.executemany(postgres_insert_query, record_list)
    conn.commit()

    message = f" Thank you for {cursor.rowcount} comment. We would reply you soon "
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

	