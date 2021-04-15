import pymysql
import numpy as np
# from toyota_transform import transform_toyota
from newcar_transform import transform_toyota
from joblib import dump, load
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

toyota=load("toyota_price.joblib")
# host='36.227.209.140'
# port=3306
# user='test'
# passwd='123456'
# db='toyota'
# charset='utf8'
# conn=pymysql.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset=charset)
# cursor=conn.cursor()


#推薦系統程式
def get_pop_recommender():
    host='1.164.249.225'
    port=3306
    user='test'
    passwd='123456'
    db='toyota'
    charset='utf8'
    conn=pymysql.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset=charset)
    cursor=conn.cursor()
    # car = pd.read_csv('popular cars.csv')
    pop_sql='''select * from pop_cars ;'''
    cursor.execute(pop_sql)
    car=cursor.fetchall()
    field_names= [i[0]for i in cursor.description]
    car=pd.DataFrame(car,columns=field_names)

    # pop_r = car.sorted(by='weighted_rating', ascending=False)[0:10]
    pop_r = car.sort_values(by='weighted_rating', ascending=False)[0:10]

    print(pop_r['brand_model'].tolist())
    cursor.close()
    conn.close()
    return (pop_r['brand_model'].tolist())

def get_content_based_recommender(user_input):
    host='1.164.249.225'
    port=3306
    user='test'
    passwd='123456'
    db='toyota'
    charset='utf8'
    conn=pymysql.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset=charset)
    cursor=conn.cursor()
    # df_desc = pd.read_csv('cars description.csv', encoding='utf-8-sig')
    desc_sql='''select * from car_des ;'''
    cursor.execute(desc_sql)
    df_desc=cursor.fetchall()
    field_names=[i[0] for i in cursor.description]
    df_desc=pd.DataFrame(df_desc,columns=field_names)
    stpwrdpath='C:/Users/TibaMe/Desktop/linebot/stopwords_for_cars.txt'
    with open(stpwrdpath,'rb') as fp:
        stopword=fp.read().decode('utf-8')
    stpwdlst=stopword.splitlines()
    count=CountVectorizer(stop_words=stpwdlst)
    vocab=count.fit(df_desc['all_cmt']) 
    count_matrix=vocab.transform(df_desc['all_cmt'])
    #df_desc['brand_model_2']=df_desc['brand_model_2'].apply(lambda x: x[:-1])
    cosine_sim = cosine_similarity(count_matrix[df_desc.loc[df_desc['brand_model_2'] == user_input].index[0],], count_matrix)
    sim_scores = list(enumerate(cosine_sim[0]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    cars_indice = [i[0] for i in sim_scores]
    content_r = df_desc['brand_model'].iloc[cars_indice].tolist()
    img = df_desc['img'].iloc[cars_indice].tolist()
    cursor.close()
    conn.close()
    print(content_r)
    print(img)
    return (content_r,img)


def get_item_based(user_input):
    #df = pd.read_csv('user_rating.csv')
    host='1.164.249.225'
    port=3306
    user='test'
    passwd='123456'
    db='toyota'
    charset='utf8'
    conn=pymysql.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset=charset)
    cursor=conn.cursor()
    user_rating_sql='''select * from user_rating ;'''
    cursor.execute(user_rating_sql)
    df=cursor.fetchall()
    field_names=[i[0] for i in cursor.description]
    df=pd.DataFrame(df,columns=field_names)

    df_drop_duplicate = df.groupby(['user_id', 'itemid']).mean().reset_index()
    sparse_matrix = df_drop_duplicate.pivot(index='itemid', columns='user_id', values='avg_rating')
    sparse_matrix = sparse_matrix.fillna(0)
    sparse_matrix_sparse = csr_matrix(sparse_matrix.values)

    # knn=NearestNeighbors(n_neighbors=10,metric='cosine')
    knn = NearestNeighbors(n_neighbors=10, metric='euclidean')
    knn_model = knn.fit(sparse_matrix_sparse)
    #cars = pd.read_csv('cars.csv')
    cars_sql='''select * from allcars ;'''
    cursor.execute(cars_sql)
    cars=cursor.fetchall()
    field_names=[i[0] for i in cursor.description]
    cars=pd.DataFrame(cars,columns=field_names)
    
    recommend_list = []
    img_list= []
    # cursor.close()
    # conn.close()
    #cars['brand_model2']=cars['brand_model2'].apply(lambda x: x[:-1])
    


    def findRecomendations(model, matrix, user_input):
        distances, indices = model.kneighbors([matrix.iloc[cars[cars['brand_model2'] == user_input].itemid.values[0], :]], n_neighbors=10)
        for i in range(0, len(distances.flatten())):
            if i == 0:
                rowDetails = cars.loc[cars['itemid'] == matrix.index[cars[cars['brand_model2'] == user_input].itemid.values[0]]]
            # print("Car: ", rowDetails.brand_model.values[0])
            else:
                rowDetails = cars.loc[cars['itemid'] == matrix.index[indices.flatten()[i]]]
                # print(" Recommendation", i, ": ")
                recommend_list.append(rowDetails.brand_model.values[0])
                img_list.append(rowDetails.img.values[0])
    findRecomendations(knn_model, sparse_matrix, user_input)
    cursor.close()
    conn.close()
    print(recommend_list)
    print(img_list)
    return (recommend_list,img_list)

def toyota_price(displacement,car_model,year,mileage,gas,color):
# if __name__=='__main__':
    toyota=load("newcar_price.joblib")
    host="1.164.249.225"
    port=3306
    user='test'
    passwd='123456'
    db='toyota'
    charset='utf8'
    conn=pymysql.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset=charset)
    cursor=conn.cursor()
    # displacement=int(input('排氣量 : '))
    # car_model=input("車型 : ").upper()
    # year=int(input("年分 : "))
    # mileage=int(input('里程 : '))
    # gas=input("燃料 : ")
    # color=input('顏色 : ').lower()
    curtime=2021
    year=2021-year
    year=(1/year)
    
    if mileage <10000:
        mileage=1
    if  20000>mileage>=10000:
        mileage=2
    if 30000>mileage>=20000:
        mileage=3
    if 40000>mileage>=30000:
        mileage=4
    if 50000>mileage>=40000:
        mileage=5
    if 60000>mileage>=50000:
        mileage=6
    if 70000>mileage>=60000:
        mileage=7
    if 80000>mileage>=70000:
        mileage=8
    if 90000>mileage>=80000:
        mileage=9
    if 100000>mileage>=90000:
        mileage=10
    if 120000>mileage>=100000:
        mileage=11
    if 150000>mileage>=120000:
        mileage=12
    if 200000>mileage>=150000:
        mileage=13
    if mileage>=200000:
        mileage=14
    mileage=1/(mileage)
    carinfo=[1]
    carinfo.append(displacement)
    carinfo.append(year)
    carinfo.append(mileage)
    car_model_sql='''select * from model where {}=1 ;'''.format(car_model)
    cursor.execute(car_model_sql)
    car_model_data=cursor.fetchall()
    # print(car_model_data[0])
    for i in car_model_data[0]:
        carinfo.append(i)
    car_gas='''select * from gas where {}=1'''.format(gas)
    cursor.execute(car_gas)
    car_gas_data=cursor.fetchall()
    for j in car_gas_data[0]:
        carinfo.append(j)
    car_color='''select * from color where {}=1'''.format(color)
    cursor.execute(car_color)
    car_color_data=cursor.fetchall()
    for k in car_color_data[0]:
        carinfo.append(k)
    carinfo_np=np.array([carinfo])
    print(carinfo_np)
    # print(carinfo_np.shape)
    cursor.close()
    conn.close()
    car_transform=transform_toyota(carinfo_np)
    res=toyota.predict(car_transform)
    print(int(res))
    # print(type(res))
    # print(carinfo_np)
    # print(car_transform)
    return int(res)

# def toyota_price(displacement,car_model,year,mileage,gas,color):
#     toyota=load("toyota_price.joblib")
#     # host='0.tcp.ngrok.io'
#     # port=17892
#     # user='test'
#     # passwd='123456'
#     # db='toyota'
#     # charset='utf8'
#     # conn=pymysql.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset=charset)
#     # cursor=conn.cursor()
#     # displacement=int(input('排氣量 : '))
#     # car_model=input("車型").upper()
#     # year=int(input("年分 : "))
#     # mileage=int(input('里程 : '))
#     # gas=input("燃料 : ")
#     # color=input('顏色 : ').lower()
#     carinfo=[1]
#     carinfo.append(displacement)
#     carinfo.append(year)
#     carinfo.append(mileage)
#     car_model_sql='''select * from model where {}=1 ;'''.format(car_model)
#     cursor.execute(car_model_sql)
#     car_model_data=cursor.fetchall()
#     # print(car_model_data[0])
#     for i in car_model_data[0]:
#         carinfo.append(i)
#     car_gas='''select * from gas where {}=1'''.format(gas)
#     cursor.execute(car_gas)
#     car_gas_data=cursor.fetchall()
#     for j in car_gas_data[0]:
#         carinfo.append(j)
#     car_color='''select * from color where {}=1'''.format(color)
#     cursor.execute(car_color)
#     car_color_data=cursor.fetchall()
#     for k in car_color_data[0]:
#         carinfo.append(k)
#     carinfo_np=np.array([carinfo])
#     # print(carinfo_np.shape)
# ###    
#     print(type(car_model))
#     car_model_lower=car_model.lower()
#     model_brand=('toyota '+car_model_lower)
    
#     rec1=get_pop_recommender()
#     rec2=get_content_based_recommender(model_brand)
#     rec3=get_item_based(model_brand)
#     str1=' '.join(rec1)
#     str2=' '.join(rec2)
#     str3=' '.join(rec3)
#     print(res)
#     print(str1)
#     print(str2)
#     print(str3)
#     alltext=str(res)+'\n'+str1+'\n'+str2+'\n'+str3+'\n'
#     print(alltext)
#     car_transform=transform_toyota(carinfo_np)
#     res=toyota.predict(car_transform)
#     # print(carinfo_np)
#     # print(car_transform)
#     cursor.close()
#     conn.close()
#     return alltext


# def toyota_price(displacement,car_model,year,mileage,gas,color):
#     # toyota=load("toyota_price.joblib")
#     # host='0.tcp.ngrok.io'
#     # port=17892
#     # user='test'
#     # passwd='123456'
#     # db='toyota'
#     # charset='utf8'
#     # conn=pymysql.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset=charset)
#     # cursor=conn.cursor()
#     # displacement=int(input('排氣量 : '))

#     # car_model=input("車型").upper()
#     # year=int(input("年分 : "))
#     # mileage=int(input('里程 : '))
#     # gas=input("燃料 : ")
#     # color=input('顏色 : ').lower()
#     carinfo=[1]
#     carinfo.append(displacement)
#     carinfo.append(year)
#     carinfo.append(mileage)
#     car_model_sql='''select * from model where {}=1 ;'''.format(car_model)
#     cursor.execute(car_model_sql)
#     car_model_data=cursor.fetchall()
#     # print(car_model_data[0])
#     for i in car_model_data[0]:
#         carinfo.append(i)
#     car_gas='''select * from gas where {}=1'''.format(gas)
#     cursor.execute(car_gas)
#     car_gas_data=cursor.fetchall()
#     for j in car_gas_data[0]:
#         carinfo.append(j)
#     car_color='''select * from color where {}=1'''.format(color)
#     cursor.execute(car_color)
#     car_color_data=cursor.fetchall()
#     for k in car_color_data[0]:
#         carinfo.append(k)
#     carinfo_np=np.array([carinfo])
#     # print(carinfo_np.shape)
#     # cursor.close()
#     # conn.close()
#     car_transform=transform_toyota(carinfo_np)
#     res=toyota.predict(car_transform)
#     print(res)
#     # print(carinfo_np)
#     # print(car_transform)
#     return res

def rcm_reply1():
    # car_model_lower=car_model.lower()
    # model_brand='toyota '+car_model
    rec1=get_pop_recommender()
    alltext='1. '+rec1[0]+'\n'+'2. '+rec1[1]+'\n'+'3. '+rec1[2]+'\n'+'4. '+rec1[3]+'\n'+'5. '+rec1[4]\
        +'\n'+'6. '+rec1[5]+'\n'+'7. '+rec1[6]+'\n'+'8. '+rec1[7]+'\n'+'9. '+rec1[8]+'\n'+'10.'+rec1[9]
    
    # str1=' '.join(rec1)
    # str2=' '.join(rec2)
    # str3=' '.join(rec3)
    # alltext=str1+'\n'+str2+'\n'+str3+'\n'
    # return rec1
    
    return alltext



def rcm_reply2(car_model):
    car_model_lower=car_model.lower()
    model_brand='toyota '+car_model_lower
    rec1=get_content_based_recommender(model_brand)
    alltext = rec1
    print(rec1)
    # alltext='1. '+rec1[0]+'\n'+'2. '+rec1[1]+'\n'+'3. '+rec1[2]+'\n'+'4. '+rec1[3]+'\n'+'5. '+rec1[4]\
        # +'\n'+'6. '+rec1[5]+'\n'+'7 .'+rec1[6]+'\n'+'8. '+rec1[7]+'\n'+'9. '+rec1[8]+'\n'+'10.'+rec1[9]
    
    return alltext

def rcm_reply3(car_model):
    car_model_lower=car_model.lower()
    model_brand='toyota '+car_model_lower
    rec1=get_item_based(model_brand)
    alltext = rec1
    # alltext='1. '+rec1[0][0]+'\n'+'2. '+rec1[0][1]+'\n'+'3. '+rec1[2]+'\n'+'4. '+rec1[3]+'\n'+'5. '+rec1[4]\
    #     +'\n'+'6. '+rec1[5]+'\n'+'7 .'+rec1[6]+'\n'+'8. '+rec1[7]+'\n'+'9. '+rec1[8]
    
    
    return alltext

# print(rcm_reply('ALTIS'))
# get_pop_recommender()
# car_eee='ALTIS'.upper()
# car_ttt=car_eee.lower()
# carcar='toyota '+car_ttt
# get_content_based_recommender('toyota altis')
# get_item_based('toyota altis')
# rcm_reply2('altis')
