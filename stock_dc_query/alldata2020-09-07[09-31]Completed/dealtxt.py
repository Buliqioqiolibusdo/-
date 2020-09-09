emp = open('stock_done.txt','a')
with open('stock_dcs.txt','r') as f:
    contents = f.readlines()
    data = ''
    for content in contents:
        emp.write(content.strip()+' ')
emp.close()
        

# print(data)