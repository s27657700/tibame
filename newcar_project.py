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
df=pd.read_csv("price_newcar.csv",encoding='utf-8')
label=df['price']
df=df.drop(['price'],axis=1)

x_train, x_test, y_train, y_test = train_test_split(df,label, test_size=0.2,random_state=9251)


x_train=transform_toyota(x_train)
x_test=transform_toyota(x_test)

model = linear_model.LinearRegression()
model.fit(x_train, y_train)
y_pred= model.predict(x_test)
print(r2_score(y_test,y_pred))
# dump(model,'newcar_price.joblib')
# print(model.coef_)
test=np.array([[1	,2500,	2016,	100000,		0,	0,	0,	0,	0,	1,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	1,	0,	0,	0,	0,	0,	0,	0,	0,	0,	1,	0,	0,	0,	0
]])
test=transform_toyota(test)
test_pred=model.predict(test)
print(int(test_pred))
print(test)