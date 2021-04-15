from toyota_sql import toyota_price

displacement=int(input('排氣量 : '))
car_model=input("車型").upper()
year=int(input("年分 : "))
mileage=int(input('里程 : '))
gas=input("燃料 : ")
color=input('顏色 : ').lower()

toyota_price(displacement,car_model,year,mileage,gas,color)