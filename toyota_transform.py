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
def transform_toyota(x):
    df=pd.read_csv("price.csv",encoding='utf-8')
    label=df['price']
    df=df.drop(['price'],axis=1)
    x_train, x_test, y_train, y_test = train_test_split(df,label, test_size=0.2,random_state=9257)
    scaler=MinMaxScaler().fit(x_train)
    x=scaler.transform(x)
    return x