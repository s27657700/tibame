import pymysql
import time
import redis

while True:
    host="36.227.210.30"
    port=3306
    user='test'
    passwd='123456'
    db='toyota'
    charset='utf8'
    conn=pymysql.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset=charset)

    r=redis.Redis(host='172.28.128.3',port = 6379 , db=0)
    cursor=conn.cursor()
    try:
        passed5min='''select model,color, count(*) from search  where  86400> (select t from search  order by t desc limit 1)-t  group by model  order by count(*) desc limit 3;'''
        cursor.execute(passed5min)
        data=cursor.fetchall()

        if len(data)==3 :
            r.set('hot1',data[0][0])
            r.set('hot2',data[1][0])
            r.set('hot3',data[2][0])
            print(data[0][0],data[1][0],data[2][0])
        else :
            time.sleep(15)
        time.sleep(15)
        
    except:
        continue
    cursor.close()
    conn.close()