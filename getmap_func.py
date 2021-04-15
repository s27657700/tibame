import csv 
import os 
import time 
import pandas as pd
from haversine import haversine, Unit

#======LINE API=========
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
# config = configparser.ConfigParser()
# config.read('config.ini')

# line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
#=======================

def getmap(address,latitude_o,longitude_o):
    df = pd.read_csv("toyota_service_map.csv", encoding='utf-8', index_col=0)
    #st_time = time.time()
    #print("地址：",address,"緯度：",latitude_o,"經度：",longitude_o)
    # print(df.columns)
    # print(df['廠名'][6])
    region_list = ['基隆市','台北市','新北市','宜蘭縣','桃園市','新竹市','新竹縣','苗栗縣','台中市','彰化縣','南投縣','雲林縣','嘉義市','嘉義縣','台南市','高雄市','屏東縣','花蓮縣','台東縣','澎湖縣','金門縣','連江縣']
    for region in region_list:
        try:
            if region in address:
                user_region=region
        except:
            return TextSendMessage(text='此位置無法查詢，請再嘗試搜尋其他位置')
    
    dist = []
    for ind in range(len(df.index)):
        dist.append(haversine((latitude_o,longitude_o),(df['緯度'][ind],df['經度'][ind])))
    #print(dist)
    min_dist = min(dist)
    min_index = dist.index(min_dist)
    a = min_index
    #print(dist)
    b = df['廠名'][a]
    #print(type(b))
    rv = df['星評'][a]
    c = str(rv).replace("\u00a0", "")
    print(c)
    #some_digit = X.values[0,:]
    contents=dict()
    contents['type']='flex'

    bubble = BubbleContainer(
    direction='ltr', 
    body=BoxComponent(
        layout='vertical',
        contents=[
            # title
            TextComponent(text= df['廠名'][a], weight='bold', size='xl'),
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
                                text=df['星評'][a],
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
                                text=df['電話'][a],
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
                                text=df['地址'][a],
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

    contents['contents']=bubble
    message = []
    message.append(LocationSendMessage(
                    title='Toyota 服務廠',
                    address=df['廠名'][a],
                    latitude=df['緯度'][a],
                    longitude=df['經度'][a]
                    ))
    message.append(FlexSendMessage(alt_text='服務廠資訊',contents=contents))
    
    # reply_arr = []         
    # locationmap = reply_arr.append(LocationSendMessage(
    #                 title='Toyota 服務廠',
    #                 address=df['廠名'][a],
    #                 latitude=df['緯度'][a],
    #                 longitude=df['經度'][a]
    #                 ))
    # mapinfo = reply_arr.append(FlexSendMessage(alt_text="server_information", contents=bubble))
    #/body/contents/1/contents/0/contents/1/text
    #print(body['contents'][1]['contents'][0]['contents'][1]['text'])
    #print(message)
    #return message