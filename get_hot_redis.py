import redis
r=redis.Redis(host='172.28.128.3',port = 6379 , db=0)
def get_hot():
    num1=r.get('hot1').decode()
    num2=r.get('hot2').decode()
    num3=r.get('hot3').decode()
    return [num1,num2,num3]
