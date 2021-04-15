from __future__ import unicode_literals
import os
import csv 
import json
import time 
import pandas as pd
import requests
# from imgurpython import ImgurClient
from haversine import haversine, Unit
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import * 

import configparser
import random
from toyota_sql_v2 import toyota_price, rcm_reply1, rcm_reply2, rcm_reply3
from toyota_image_transform import image_transform
from connect_producer import send_info
from get_hot_redis import get_hot
from detection_custom import test, pred
# from V3-copy.TensorFlow-2.x-YOLOv3-master.yolov3.utilscopy import * #detect_image, detect_realtime, detect_video, Load_Yolo_model, detect_video_realtime_mp
# from V3-copy.TensorFlow-2.x-YOLOv3-master.yolov3.configs import *
from yolov3.utils import detect_image, detect_realtime, detect_video, Load_Yolo_model, detect_video_realtime_mp
from yolov3.configs import *
#from getmap_func import getmap

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

#imgur_id&secret
# client = ImgurClient((config.get('imgur','client_id')),(config.get('imgur', 'client_secret')))

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
#handle text message
def handle_text_message (event):

    #button 1
    text = event.message.text
    if text == "車輛辨識":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請上傳照片")
            )
    #button 2
    elif text == "二手車價格預測":        
        c=rcm_reply1()
        reply_arr = []
        reply_arr.append(TextSendMessage(text="請依照格式輸入車輛條件\
                \n格式為:\
                \n排氣量,車型,年分,里程數,燃料,顏色\
                \n範例:\
                \n2000,altis,2015,20000,gas,red\
                \n文字部分請使用英文"))
        reply_arr.append(TextSendMessage(text="目前全台網友熱搜車款前10名: \n{}".format(c)))

        line_bot_api.reply_message(
            event.reply_token,
            reply_arr
            )
    #button 3
    elif text == "維修保養廠資訊":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請傳送所在位置訊息")
            )
    
    # button 2 user msg
    elif len(text.split(',')) == 6:        
        a = text.split(',') #a is a list
        x=0
        for i in a:
            try:
                i = i.replace("\n","")
            except:
                pass
            a[x]=i
            x+=1
        displacement=int(a[0])
        car_model=a[1].upper()
        year=int(a[2])
        mileage=int(a[3])
        gas= a[4]
        color=a[5].lower()
        car_model_lower=a[1].lower()
        send_info(car_model,year,mileage,gas,color)

        toyota_model_list = ['4RUNNER','ALPHARD','ALTIS',
        'AT2EPN','AURIS','CAMRY','CELICA','CHR','COASTER',
        'COROLLA SPORT','CORONA','CROSS','CROWN','DYNA',
        'EXSIOR','FT86','GRANVIA','HIACE','HILUX','HINO',
        'INNOVA','LAND CRUISER PRADO','PRADO','PREMIO',
        'PREVIA','PRIUS','RAV4','SIENNA','SIENTA','SOLARA',
        'SUPRA','TACOMA','TERCEL','TUNDRA','VIOS','WISH',
        'YARIS','ZACE']
        if car_model not in toyota_model_list:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="此為無效車型")
            ) 

        else:
            b=toyota_price(displacement,car_model,year,mileage,gas,color)                    
            e=rcm_reply3(car_model_lower)
            carousel_string = """
            {
                "type": "carousel",
                "contents": [
                {
                    "type": "bubble",
                    "hero": {
                    "type": "image",
                    "url": "https://hotaicdn.azureedge.net/toyotaweb/CMS_202101271119240B341583.jpg",
                    "size": "full",
                    "aspectMode": "cover"
                    },
                    "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                        "type": "text",
                        "text": "Toyota VIOS "
                        }
                    ]
                    },
                    "size": "micro"
                },
                {
                    "type": "bubble",
                    "size": "micro",
                    "hero": {
                    "type": "image",
                    "url": "https://media.ed.edmunds-media.com/bmw/3-series/2011/oem/2011_bmw_3-series_convertible_335i_fq_oem_2_500.jpg",
                    "size": "full",
                    "aspectMode": "cover"
                    },
                    "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                        "type": "text",
                        "text": "BMW 3-Series Convertible"
                        }
                    ]
                    }
                },
                {
                    "type": "bubble",
                    "size": "micro",
                    "hero": {
                    "type": "image",
                    "url": "https://autos.yahoo.com.tw/y/r/w1200/iw/MMT/car/cd0cad3b30c1a4feac4d533df5003c04_1200.jpg",
                    "size": "full",
                    "aspectMode": "cover"
                    },
                    "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                        "type": "text",
                        "text": "Ford ESCORT"
                        }
                    ]
                    }
                }
                ]
            }"""
            # template = CarouselTemplate(
            # columns=[
            #     CarouselColumn(
            #         bubble = BubbleContainer(
            #             size='micro',
            #             hero=ImageComponent(
            #                 url=e[1][0].replace('\r',''),
            #                 size='full',
            #                 aspect_mode='cover'
            #             ),
            #             body=BoxComponent(
            #                 layout='vertical',
            #                 contents=[
            #                     TextComponent(
            #                         text=e[0][0])]))),
            #     CarouselColumn(
            #         bubble = BubbleContainer(
            #             size='micro',
            #             hero=ImageComponent(
            #                 url=e[1][1].replace('\r',''),
            #                 size='full',
            #                 aspect_mode='cover'
            #             ),
            #             body=BoxComponent(
            #                 layout='vertical',
            #                 contents=[
            #                     TextComponent(
            #                         text=e[0][1]
            #                     )
            #                 ]
            #             ))
            #             ),
            #     CarouselColumn(
            #         bubble = BubbleContainer(
            #             size='micro',
            #             hero=ImageComponent(
            #                 url=e[1][2].replace('\r',''),
            #                 size='full',
            #                 aspect_mode='cover'
            #             ),
            #             body=BoxComponent(
            #                 layout='vertical',
            #                 contents=[
            #                     TextComponent(
            #                         text=e[0][2]
            #                     )
            #                 ]
            #             ))),
            # ])

            reply_arr = []
            # reply_arr.append(TextSendMessage(text="輸入成功"))
            reply_arr.append(TextSendMessage(text="預測價格為 : {}".format(b)))
            reply_arr.append(TextSendMessage(text="專屬於你的推薦:"))
            reply_arr.append(FlexSendMessage(alt_text="car_re", contents=json.loads(carousel_string)))
            # reply_arr.append(FlexSendMessage(alt_text="car_re", contents=template))
            # reply_arr.append(TextSendMessage(text= b )
            line_bot_api.reply_message(event.reply_token,reply_arr)
    elif text == "熱搜排行榜":
        hot_text = '1.'+get_hot()[0].upper()+'\n'+'2.'+get_hot()[1].upper()+'\n'+'3.'+get_hot()[2].upper()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='熱搜排名:'+'\n'+hot_text)
            )

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="無法辨識訊息")
            ) 

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message (event):
    if event.message.type=='image':
        user_id = line_bot_api.get_profile(event.source.user_id)
        message_content = line_bot_api.get_message_content(event.message.id)
        # 取得 struct_time 格式的時間
        t = time.localtime()
        # 依指定格式輸出
        tresult = time.strftime("%m%d%Y%H%M%S", t)

        with open(('./img/image'+ tresult +'.jpg'), 'wb') as fd:        
            for chunk in message_content.iter_content():
                fd.write(chunk)

        #辨識結果        
        # car_model_nparr=image_transform('./img/image'+ tresult +'.jpg')
        car_model_nparr=pred('./img/image'+ tresult +'.jpg')

        if car_model_nparr == 'please upload car image again'or len(car_model_nparr) ==0:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="484想騙我阿\n請上傳車輛圖片~")
                ) 
        else:
            # for i in range(len(car_model_nparr))
            car_model = car_model_nparr[0]
            df = pd.read_csv("./carinfo_vgg16.csv", encoding='utf-8', index_col=False)

            bubble = BubbleContainer(
                direction='ltr',
                hero=ImageComponent(
                    # url='https://autos.yahoo.com.tw/p/r/w1200/car-trim/March2019/5433211bbfe874461faba74d5989ad97.jpeg',
                    url = df.iloc[car_model]['圖片'],
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover',
                    action=URIAction(uri='http://linecorp.com/', label='label')
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        # title
                        TextComponent(text=df.iloc[car_model]['車型'], weight='bold', size='xl'),
                        
                        # info
                        BoxComponent(
                            layout='vertical',
                            margin='lg',
                            spacing='sm',
                            contents=[
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='燃料種類',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=2
                                        ),
                                        TextComponent(
                                            # text='燃料種類',
                                            text= df.iloc[car_model]['燃料'],
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5
                                        )
                                    ],
                                ),
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='最大馬力',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=2
                                        ),
                                        TextComponent(
                                            # text='最大馬力',
                                            # text= df.iloc[car_model]['最大馬力'],
                                            text= ((df.iloc[car_model]['最大馬力'])+'(ps/rpm)'),
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5
                                        )
                                    ],
                                ),
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='平均油耗',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=2
                                        ),
                                        TextComponent(
                                            # text='平均油耗',
                                            # text=float(df.iloc[car_model]['平均油耗']),
                                            text=str(df.iloc[car_model]['平均油耗'])+'(km/l)',
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5
                                        )
                                    ],
                                ),
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='排氣量',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=2
                                        ),
                                        TextComponent(
                                            # text='排氣量',
                                            # text=int(df.iloc[car_model]['排氣量']),
                                            text= (str(df.iloc[car_model]['排氣量']) + 'c.c.'),
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5
                                        )
                                    ],
                                ),                                                                                    
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='新車價格',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=2
                                        ),
                                        TextComponent(
                                            # text='新車價格',
                                            # text= int(df.iloc[car_model]['新車價格']),
                                            text=(str(df.iloc[car_model]['新車價格']) + '萬'),
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5,
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                footer=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        # callAction
                        ButtonComponent(
                            style='link',
                            height='sm',
                            # action=URIAction(label='更多資訊', uri='https://autos.yahoo.com.tw/new-cars/trim/toyota-corolla-altis%28new%29-2019-1.8%E5%B0%8A%E7%88%B5
                            action=URIAction(label='更多資訊', uri=df.iloc[car_model]['網址']),
                        ),
                        # # separator
                        # SeparatorComponent(),
                        # # websiteAction
                        # ButtonComponent(
                        #     style='link',
                        #     height='sm',
                        #     action=URIAction(label='WEBSITE', uri="https://example.com")
                        # )
                    ]
                ),
            )
            car_model_lower=df.iloc[car_model]['車型']
            # car_model_lower=df[[int(car_model),'車型']]
            # print(car_model_lower)
            d=rcm_reply2(car_model_lower)
            

            # url1 = d[1][0].replace('\r','')
            # url2 = d[1][1].replace('\r','')
            # print(url2)
            # url2 = url2_1.replace(' ', '')

            carousel_string = """
            {
                "type": "carousel",
                "contents": [
                {
                    "type": "bubble",
                    "hero": {
                    "type": "image",
                    "url": "https://hotaicdn.azureedge.net/toyotaweb/CMS_2021010815101353124344.jpg",
                    "size": "full",
                    "aspectMode": "cover"
                    },
                    "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                        "type": "text",
                        "text": "Toyota C-HR "
                        }
                    ]
                    },
                    "size": "micro"
                },
                {
                    "type": "bubble",
                    "size": "micro",
                    "hero": {
                    "type": "image",
                    "url": "https://new.nissan.com.tw/upload/model/SENTRA/360/orange2tone/1.jpg",
                    "size": "full",
                    "aspectMode": "cover"
                    },
                    "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                        "type": "text",
                        "text": "Nissan SENTRA"
                        }
                    ]
                    }
                },
                {
                    "type": "bubble",
                    "size": "micro",
                    "hero": {
                    "type": "image",
                    "url": "https://autos.yahoo.com.tw/y/r/w1200/iw/MMT/car/529cf083c5943e98c721748c340c3b1c_1200.jpg",
                    "size": "full",
                    "aspectMode": "cover"
                    },
                    "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                        "type": "text",
                        "text": "Honda City"
                        }
                    ]
                    }
                }
                ]
            }"""

            # template = CarouselTemplate(
            #     columns=[
            #         CarouselColumn(
            #             bubble = BubbleContainer(
            #                 size='micro',
            #                 hero=ImageComponent(
            #                     url='https://hotaicdn.azureedge.net/toyotaweb/CMS_2021010815101353124344.jpg',
            #                     size='full',
            #                     aspect_mode='cover'
            #                 ),
            #                 body=BoxComponent(
            #                     layout='vertical',
            #                     contents=[
            #                         TextComponent(
            #                             text= 'Toyota C-HR'
            #                         )
            #                     ]
            #                 ))
            #                 ),
            #         CarouselColumn(
            #             bubble = BubbleContainer(
            #                 size='micro',
            #                 hero=ImageComponent(
            #                     url='https://new.nissan.com.tw/upload/model/SENTRA/360/orange2tone/1.jpg',
            #                     size='full',
            #                     aspect_mode='cover'
            #                 ),
            #                 body=BoxComponent(
            #                     layout='vertical',
            #                     contents=[
            #                         TextComponent(
            #                             text='Nissan SENTRA'
            #                         )
            #                     ]
            #                 ))
            #                 ),
            #         CarouselColumn(
            #             bubble = BubbleContainer(
            #                 size='micro',
            #                 hero=ImageComponent(
            #                     url='https://autos.yahoo.com.tw/y/r/w1200/iw/MMT/car/529cf083c5943e98c721748c340c3b1c_1200.jpg',
            #                     size='full',
            #                     aspect_mode='cover'
            #                 ),
            #                 body=BoxComponent(
            #                     layout='vertical',
            #                     contents=[
            #                         TextComponent(
            #                             text='Honda City'
            #                         )
            #                     ]
            #                 ))),
            #     ]
            # )
                        
            reply_arr=[]
            reply_arr.append(FlexSendMessage(alt_text="car_information", contents=bubble))
            reply_arr.append(TextSendMessage(text="與"+df.iloc[car_model]['車型']+"相似車款推薦:"))
            # reply_arr.append(FlexSendMessage(alt_text="car_re", contents=template))
            reply_arr.append(FlexSendMessage(alt_text="car_re", contents=json.loads(carousel_string)))
            line_bot_api.reply_message(event.reply_token,reply_arr)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message (event):
    if event.message.type=='location':
        address = event.message.address
        latitude = event.message.latitude
        longitude = event.message.longitude

        df_map = pd.read_csv("toyota_service_map.csv", encoding='utf-8', index_col=0)
        region_list = ['基隆市','台北市','新北市','宜蘭縣','桃園市','新竹市','新竹縣','苗栗縣','台中市','彰化縣','南投縣','雲林縣','嘉義市','嘉義縣','台南市','高雄市','屏東縣','花蓮縣','台東縣','澎湖縣','金門縣','連江縣']
        for region in region_list:
            try:
                if region in address:
                    user_region=region
            except:
                return TextSendMessage(text='此位置無法查詢，請再嘗試搜尋其他位置')
        
        dist = []
        for ind in range(len(df_map.index)):
            dist.append(haversine((latitude,longitude),(df_map['緯度'][ind],df_map['經度'][ind])))
        #print(dist)
        min_dist = min(dist)
        min_index = dist.index(min_dist)
        a = min_index
        #print(dist)
        rv = df_map['星評'][a]
        rw = str(rv).replace("\u00a0", "")

        # contents=dict()
        # contents['type']='flex'

        bubble = BubbleContainer(
            direction='ltr', 
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text=df_map['廠名'][a], weight='bold', size='xl'),
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='評價',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text= rw,                                        
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='電話',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        #text='電話',
                                        text=df_map['電話'][a],
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='地址',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        #text='地址',
                                        text=df_map['地址'][a],
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),                            
                        ],
                    )
                ],
            ),
        )        

        # contents['contents']=bubble
        reply_arr=[]
        #locationmap = 
        reply_arr.append(LocationSendMessage(
                        title='Toyota 服務廠',
                        address=df_map['廠名'][a],
                        latitude=df_map['緯度'][a],
                        longitude=df_map['經度'][a]
                        ))

        reply_arr.append(FlexSendMessage(alt_text='服務廠資訊',contents=bubble))            
        line_bot_api.reply_message(event.reply_token, reply_arr)    
 
if __name__ == "__main__":
    app.run()