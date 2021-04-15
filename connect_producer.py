from confluent_kafka import Producer
import sys
import time
import pandas as pd
import numpy as np 

# 用來接收從Consumer instance發出的error訊息
def error_cb(err):
    print('Error: %s' % err)
    



# 主程式進入點
def send_info(car_model,year,mileage,gas,color):
# if __name__=='__main__':
    # 步驟1. 設定要連線到Kafka集群的相關設定
    props = {
        # Kafka集群在那裡?
        'bootstrap.servers': 'localhost:9092',  # <-- 置換成要連接的Kafka集群
        'error_cb': error_cb                    # 設定接收error訊息的callback函數
    }
    # 步驟2. 產生一個Kafka的Producer的實例
    producer = Producer(props)
    # 步驟3. 指定想要發佈訊息的topic名稱
    topicName = 'project'
    # msgCounter = 0
    # car_model=car_model.encode()
    # displacement=2400
    # car_model='altis'
    # year=2017
    # mileage=35000
    # gas='gas'
    # color='black'
    # gas=gas.encode()
    # color=color.encode()
    carinfo='{},{},{},{},{}'.format(car_model,color,year,mileage,gas)
    # try:
        # produce(topic, [value], [key], [partition], [on_delivery], [timestamp], [headers])
    producer.produce(topicName,carinfo)
    print(carinfo)
    producer.flush()
    # except BufferError as e:
    #     # 錯誤處理
    #     # sys.stderr.write('%% Local producer queue is full ({} messages awaiting delivery): try again\n'
    #     #                  .format(len(producer)))
    #     print ('try again')

    # except Exception as e:
    #     print ( 'try again')
    # 步驟5. 確認所在Buffer的訊息都己經送出去給Kafka了
    producer.flush()
    # return 'ok'
# displacement=2400
# car_model='rav4'
# year=2017
# mileage=35000
# gas='gas'
# color='black'
# send_info(car_model,year,mileage,gas,color)