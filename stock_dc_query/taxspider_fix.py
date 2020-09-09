 #coding = utf-8
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import datetime
import json 
from tesserocr import image_to_text
from PIL import Image
import re,os

starttime = datetime.datetime.now()
# path ='./Desktop/spidercode/stock_dc_query'
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
now_time = datetime.datetime.now().strftime('%Y-%m-%d[%H-%M]')
# 选择爬取范围
while True:  
    choice = input('>>>请选择爬取全部（all）或中证500（500）亦或过滤免滑样本（zdc）：')
    if  choice == 'all':
        choice_all = input('选择四千样本（任意键）或者两千样本（2000）：')
        if choice_all =='2000':
            dir_name = './data2000%s'%(now_time)
            logs_file ='./data2000%s/logs.txt'%(now_time)
            ban_file = './data2000%s/ban_stock.txt'%(now_time)
            stock_dc_file = './data2000%s/stock_dc.txt'%(now_time)
            stock_file = './StockCodeName/stock_2000.json'
            zdc_file = './StockCodeName/zdc_stock_2000.json'
            break
        else:
            dir_name = './alldata%s'%(now_time)
            logs_file ='./alldata%s/logs.txt'%(now_time)
            ban_file = './alldata%s/ban_stock.txt'%(now_time)
            stock_dc_file = './alldata%s/stock_dc.txt'%(now_time)
            stock_file = './StockCodeName/stock_all4000.json'
            zdc_file = './StockCodeName/zdc_stock_all4000.json'
            break
    elif choice == '500':
        dir_name = './data500%s'%(now_time)
        logs_file ='./data500%s/logs.txt'%(now_time)
        ban_file = './data500%s/ban_stock.txt'%(now_time)
        stock_dc_file = './data500%s/stock_dc.txt'%(now_time)
        stock_file = './StockCodeName/stock_zz500.json'
        zdc_file = './StockCodeName/zdc_stock_500.json'
        break
    elif choice == 'zdc':
        confirm_choice = input('>>>是否已经初级过滤allstock并保存在./StockCodeName文件中?[y/n]:')
        if confirm_choice == 'y':
            dir_name = './zdcdata%s'%(now_time)
            logs_file ='./zdcdata%s/logs.txt'%(now_time)
            ban_file = './zdcdata%s/ban_stock.txt'%(now_time)
            stock_dc_file = './alldata%s/stock_dc.txt'%(now_time)
            stock_file = './StockCodeName/zdc_stock_all4000.json'
            zdc_file = './StockCodeName/zdc_stock_浓缩.json'
            break
        else:    
            continue
    elif choice =='exit':
        raise SystemExit
    else:
        print('>>>Error！！命令无效<<<。\n提示：退出命令（exit）')
        continue


url = 'http://system.zb12.net/'
browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)
browser.maximize_window()
os.mkdir(dir_name)

#登录页面验证操作
while True:
    try :
        order_element = browser.find_element_by_xpath("//*[@id='clause']/tbody/tr[2]/td/input[1]")
        order_element.click()
        break
    except:
        browser.get(url)
        account = 'shiwan'
        password = '313233'

        account_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#username")))
        account_element.send_keys(account)
        password_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#password")))
        password_element.send_keys(password)

        img_element=browser.find_element_by_id("validateImg")#定位验证码
        browser.save_screenshot('printscreen.png') 
        location = img_element.location  # 获取验证码x,y轴坐标
        size = img_element.size  # 获取验证码的长宽
        rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
        i = Image.open("printscreen.png")  # 打开截图
        frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
        frame4.save('validate.png') # 保存我们接下来的验证码图片 进行打码
        image = Image.open('validate.png')  

        result = image_to_text(image)   
        result = re.findall('[\u4e00-\u9fa5a-zA-Z0-9]+',result,re.S) #只要字符串中的中文，字母，数字
        result_str = "".join(result)
        validate_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#validate")))
        validate_element.send_keys(result_str)

        login_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#submitbutton")))
        login_element.click()
        time.sleep(1)
os.remove('validate.png')
os.remove('printscreen.png')

with open(stock_file,'r') as f:
    code_data = json.load(f)

with open(stock_dc_file,'a+') as g:
    g.write('-*-'*12+'\r\n')
    g.write('>>表当前时间段有效，仅供次日参考<<'.center(30)+'\r\n'+now_time.center(30)+'\r\n')

logs = open(logs_file,'a+')
logs.write('-*-'*10+'\r\n')
logs.write(now_time+'\r\n')


count = 1
e_count = 1
b_count = 1
name_list = ['--',]
zdc_dict = {}

# #点选左边框快速交易选框
browser.switch_to.frame(browser.find_element_by_css_selector("frameset frameset frame[name = 'leftFrame']"))
order_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.leftmenu ul:nth-child(2) li:nth-child(3) a")))
# order_element = browser.find_element_by_xpath("//a[contains(.,'快速下单')]")
order_element.click()
browser.switch_to.parent_frame()     #需要切换到父frame
browser.switch_to.frame('stockMain')

while True:
    try:

        buy_code_element =wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#buy_code")))
        buy_code_element.clear()
        # 检查是否休市
        # try:
        #     station_element = browser.find_element_by_xpath("//*[@id = 'ordertitle'][contains(.,'休')]")   #不明白为什么匹配不上？？？？？
        #     print('休市中，请等待')
        #     raise SystemExit
        # except:
        #     print('继续')
        #     raise SystemExit
    except Exception as error:
        print(error)
        print('暂未开市，请稍等！')
        time.sleep(100)
        browser.refresh()
        continue 
    try:
        for code,name in code_data.items():
            # try:
                #输入代码
            buy_code_element =wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#buy_code")))
            # buy_code_element =wait.until(EC.((By.CSS_SELECTOR,"input#buy_code")))
            # try:
            buy_code_element.clear()
            buy_code_element.send_keys(code)
            # except Exception as error:
            #     print(error)
            #     time.sleep(600)
            #     continue
            time.sleep(0.8)
            # except:
            #     print('暂未开市，请等待！')
            #     browser.close()
            #     raise SystemExit
            print(code+name.strip().rjust(10)+'\t'+'#'*15+'\t'+'Count:%d'%(count)+'\t',end='')
            logs.write(code+name.strip().rjust(8)+'\t'+' '*3+'#'*15+'Count:%d'%(count)+'#'*15+'\t')
            count +=1
            try:
                #点选个股
                click_stock_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"tr[id*= '{}']".format(code))))
                click_stock_element.click()
                time.sleep(2)
            # except Exception as e:
            #     click_stock_element_re = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"tr[id*= '{}']".format(name))))
            #     time.sleep(0.5)
            #     click_stock_element_re.click()
            except :
                print('   <点选不了>')
                logs.write('<点选不了>'+'\r\n')
                continue   
            #获取代码滑点
            buy_dc = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"span#buy_dc"))).text
            # print(buy_code_element)
            #获取代码名称
            get_name =wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"td#buy_name"))).text

            if  str(get_name) in name_list:
                #点选后若个股名称未改变则写入个股禁止文档
                with open(ban_file,'a+') as i:
                    i.write(get_name+'\t'+'  <禁止交易>'+'\t'+'   Count:%d'%(b_count)+'\t'+'\r\n')
                    b_count+=1
                    print('<禁止交易>')
                logs.write('<禁止交易>'+'\t'+'\r\n')
                continue
            else:
                #点选后个股变化则个股可选
                print('   <滑点:%s>'%(buy_dc))
                logs.write('滑点:%s'%(buy_dc)+'\r\n')
                # print(name_list)
                name_list.append(get_name)
                #判断滑点是否为千零
                if buy_dc ==str('0 ‰'):
                    with open(stock_dc_file,'a+') as g:
                        g.write(get_name.strip()+'\t'+'#'*10+'\t'+'<滑点:'+str(buy_dc)+'>'+'\t'+'Count:%d'%(e_count)+'\r\n')
                        e_count+=1
                    zdc_dict[code] = name
        break
    except Exception:
        print('午盘休息时间..')
        continue


endtime = datetime.datetime.now()
now_end_time =datetime.datetime.now().strftime('%Y-%m-%d[%H-%M]')
with open(zdc_file,'w') as o:
    zdc_json = json.dumps(zdc_dict)
    o.write(zdc_json)
with open(stock_dc_file,'a+') as g:
    g.write('>>>表当前时间段有效，仅供次日参考<<<'+now_end_time+'\r\n')
    g.write('-*-'*10+'\r\n')


logs.close()
os.rename(dir_name,dir_name+'Completed')
# browser.close()


print('用时：',endtime-starttime)
print('<<< Completed！>>>')






