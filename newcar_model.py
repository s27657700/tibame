import pandas as pd
from sklearn import linear_model
from sklearn.metrics import r2_score,mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
import numpy as np 
from sklearn.model_selection import cross_val_score
from joblib import dump, load
import pymysql
from newcar_transform import transform_toyota


df=pd.read_csv("price_age.csv",encoding='utf-8')
# print(df.corr())
label=df['price']
df=df.drop(['price'],axis=1)


x_train, x_test, y_train, y_test = train_test_split(df,label, test_size=0.1,random_state=0)


x_train=transform_toyota(x_train)
x_test=transform_toyota(x_test)

model = linear_model.LinearRegression()
model.fit(x_train, y_train)
dump(model, 'newcar_price.joblib') 
y_pred= model.predict(x_test)
print(r2_score(y_test,y_pred))

a=1/(3)
print(a)
test=np.array([[
    1,2400,0.090909090909091,a,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0
]])
# print(test)
test=transform_toyota(test)
test_pred=model.predict(test)
print(int(test_pred))
# print(test)