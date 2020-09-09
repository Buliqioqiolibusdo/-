import tushare as ts
import json

#查看数据数量   
with open('stock_2000.json','r') as f:
    all_2000 = json.load(f)

with open('stock_all4000.json','r') as m:
    all_4000 = json.load(m)

with open('stockdata.json','r') as h:
    data = json.load(h)
f_num = 0
m_num = 0
# h_num = 0

for i in all_2000.items():
    f_num +=1

for i in all_4000.items():
    m_num +=1

# for i in data.items():
#     h_num +=1

print(f_num,m_num,)


#获取数据
data = ts.get_stock_basics()

data = data.loc[(data['pe']>0)&(data['pe']<60)]
print(data)
bol = data['name'].str.contains('ST')
filter_data = data[~bol]['name']
print(filter_data)
filter_data.to_json('stock_all_2000.json')
