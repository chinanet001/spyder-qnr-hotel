from selenium import webdriver
from selenium.webdriver import ActionChains
from time import sleep
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
# from mysql import cursor,connect
from bs4 import BeautifulSoup
import random
import datetime
import pandas as pd
import csv

current_month = datetime.date.today().month
last_month = current_month - 1
if current_month < 10:
    current_month = '0' + str(current_month)
if last_month < 10:
    if last_month == 0:
        last_month = '12'
    elif last_month < 10:
        last_month = '0' + str(last_month)

def get_hotel_id():
    shi = ['chaozhou','shenzhen', 'guangzhou', 'dongguan', 'foshan', 'zhongshan', 'zhuhai', 'shantou', 'qingyuan', 'heyuan',
        'zhaoqing', 'yunfu', 'shaoguan', 'meizhou', 'jiangmen', 'maoming', 'yangjiang', 'zhanjiang', 'huizhou_guangdong', 'shanwei', 'jieyang']
    profile = get_profile()
    driver = webdriver.Firefox(profile)
    url_hotel_list = 'http://hotel.qunar.com/city/'
    pattern_yema = 'data-page="([0-9]+)"'
    yema_pattern = re.compile(pattern_yema)
    for s in shi:
        sql = "insert into qne_hotel_id(qne_hotel_id,shi) VALUES "
        pattern_id = 'id="js_plugin_tag_' + s + '_([0-9]+)"'
        id_pattern = re.compile(pattern_id)
        url_hotel_list_shi = url_hotel_list + s + "/"
        driver.get(url_hotel_list_shi)
        ele = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "hotel_item")))
        html = driver.page_source
        yema = yema_pattern.findall(html)[-2]
        i = 0
        while i<int(yema):
            js="var q=document.documentElement.scrollTop=10000"
            driver.execute_script(js)
            sleep(2)
            js="var q=document.documentElement.scrollTop=5000"
            driver.execute_script(js)
            sleep(0.5)
            html_hotel_id = BeautifulSoup(driver.page_source, 'lxml')
            hotel_id_list = id_pattern.findall(driver.page_source)
            hotel_id_set = set(hotel_id_list)
            for id in hotel_id_set:
                sql = sql + "('" + id + "','" + s + "')" + ","
            if i == (int(yema)-1):
                pass
            else:
                ac = driver.find_element_by_xpath("//span[text()='下一页']")
                ActionChains(driver).move_to_element(ac).perform()#定位鼠标到指定元素
                ac.click()
            sleep(1)
            i = i+1
            print(i)
        sql = sql[:-1]
        cursor.execute(sql)
        connect.commit()
        print('成功插入', cursor.rowcount, '条数据')
        driver.close()
        profile = get_profile()
        driver = webdriver.Firefox(profile)

def get_hotel_details_comments(hotel_id_list,done_list):

    starttime = datetime.datetime.now()
    profile = get_profile()
    time_mark = 1
    for id,s in hotel_id_list:
        if [id,s] not in done_list:
            try:
                sql_details = "insert into qnr_hotel_details VALUES "
                sql_commnets = "insert into qnr_hotel_comments VALUES "
                nowtime = datetime.datetime.now()
                timeminus = ((nowtime-starttime).seconds)/60
                if (timeminus > 5*time_mark):
                    profile = get_profile()
                    time_mark = time_mark+1
                driver = webdriver.Firefox(profile)
                driver.set_page_load_timeout(4)
                url = 'http://hotel.qunar.com/city/'+s+'/dt-'+id+"/"
                try:
                    driver.get(url)
                except Exception:
                    driver.execute_script("window.stop()")
                sleep(1.5)
                try:
                    driver.find_element_by_id('QunarPopBox')
                    sleep(1.5)
                    driver.delete_all_cookies()
                    driver.close()
                    continue
                except Exception:
                    try:
                        ac = driver.find_element_by_css_selector('a[class="handler js-order-time"]')
                    except Exception:
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'lxml')
                        hotel_name = soup.find_all('div', {'id': 'detail_pageHeader'})[0].find_all('h2')[0].find_all('span')[0].text.replace("'","\\'")
                        dangci = soup.find_all('div', {'id': 'detail_pageHeader'})[0].find_all('h2')[0].find_all('em')[0]['title']
                        addr = soup.find_all('div', {'id': 'detail_pageHeader'})[0].find_all('p')[0].find('span')['title'].replace('\'','')
                        try:
                            qu = soup.find_all('div', {'id': 'detail_pageHeader'})[0].find_all('p')[0].find('cite').text
                        except Exception:
                            qu = ''
                        pattern_jw = "var hotelBPoint=\[([0-9]+)\.([0-9]+),([0-9]+)\.([0-9]+)\];*?"
                        jw_pattern = re.compile(pattern_jw)
                        try:
                            jw = jw_pattern.findall(driver.page_source)[0]
                            jingdu = jw[0] + "." + jw[1]
                            weidu = jw[2] + "." + jw[3]
                        except Exception:
                            jingdu = ''
                            weidu = ''
                        sql_details = sql_details + "('%s','%s','%s','%s','%s','%s','%s','%s')" % (id, s, qu, hotel_name, dangci, addr, jingdu, weidu)
                        sql_commnets = sql_commnets + "('%s','%s','%s','%s','%s')" % (str(id), s, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), 'zero comment', 'zero comment')
                        cursor.execute(sql_details)
                        cursor.execute(sql_commnets)
                        connect.commit()
                        print('insert zero comment,only details')
                        driver.close()
                        continue
                    ac.click()
                    sleep(1)
                    html = driver.page_source
                    soup = BeautifulSoup(html,'lxml')
                    hotel_name = soup.find_all('div',{'id':'detail_pageHeader'})[0].find_all('h2')[0].find_all('span')[0].text.replace("'","\\'")
                    dangci = soup.find_all('div',{'id':'detail_pageHeader'})[0].find_all('h2')[0].find_all('em')[0]['title']
                    addr = soup.find_all('div',{'id':'detail_pageHeader'})[0].find_all('p')[0].find('span')['title'].replace('\'','')
                    try:
                        qu  = soup.find_all('div',{'id':'detail_pageHeader'})[0].find_all('p')[0].find('cite').text
                    except Exception:
                        qu=''
                    pattern_jw = "var hotelBPoint=\[([0-9]+)\.([0-9]+),([0-9]+)\.([0-9]+)\];*?"
                    jw_pattern = re.compile(pattern_jw)
                    try:
                        jw = jw_pattern.findall(driver.page_source)[0]
                        jingdu = jw[0] + "." + jw[1]
                        weidu = jw[2] + "." + jw[3]
                    except Exception:
                        jingdu = ''
                        weidu = ''
                    sql_details = sql_details + "('%s','%s','%s','%s','%s','%s','%s','%s')" % (id,s,qu,hotel_name,dangci,addr,jingdu,weidu)
                    print(sql_details)
                    try:
                        yema_box = soup.find('div',{'class':'js-pager page-cont'}).find_all('a',{'class':'num'})
                        yema = yema_box[-2]['data-pageno']
                    except Exception:
                        yema_box = soup.find('div', {'class': 'js-pager page-cont'}).find_all('span', {'class': 'num'})
                        yema = yema_box[0].text
                        print(yema)
                    for i in range(int(yema)):
                        soup = BeautifulSoup(driver.page_source,'lxml')
                        comment_list = soup.find('div',{'class':'js-feed-list'}).find_all('div',{'class':'b_ugcfeed clrfix js-feed'})
                        for comment_box in comment_list:
                            daytime = comment_list.find('li',{'class':'item pubdate'}).find('a')['title']+":00"
                            daytime = daytime.replace('日','').replace('月','-').replace('年','-')
                            try:
                                type = comment_box.find('ul',{'class':'checktype clrfix js-checkin'}).text
                            except Exception:
                                type=''
                            try:
                                comment = comment_box.find('p',{'class':'js-full'}).text
                                pattern = re.compile('[\r\n]+')
                                comment_clean = pattern.sub('',comment).replace('\'','').replace('\\','')
                            except Exception:
                                comment_clean='no comment'
                            sql_commnets = sql_commnets + "('%s','%s','%s','%s','%s')," % (str(id),s,daytime,type,comment_clean)
                        try:
                            page_next = driver.find_element_by_css_selector('div[class="ui-page"]').find_element_by_css_selector('a[class="num icon-tag"]')
                            page_next.click()
                            tim = random.randint(0.5,1)
                            sleep(tim)
                        except Exception:
                            continue
                    print(sql_commnets[:-1])
                    cursor.execute(sql_details)
                    cursor.execute(sql_commnets[:-1])
                    connect.commit()
                driver.close()
            except Exception  as e:
                print(e)
                continue

def incre_cmt(hotel_id_list,done_list):
    # starttime = datetime.datetime.now()
    # time_mark = 1
    for id,s in hotel_id_list:
        if [id,s] not in done_list:
            try:
                qnrresult = open('qnr.csv', 'a+', newline='')
                csv_writer = csv.writer(qnrresult)
                done = open('qnr-done.csv', 'a+', newline='')
                csv_writer_done = csv.writer(done)
                sql_commnets = "insert into qnr_hotel_comments VALUES "
                # nowtime = datetime.datetime.now()
                # timeminus = ((nowtime-starttime).seconds)/60
                # if (timeminus > 5*time_mark): #此处设定大约5分钟更换一次代理
                #     time_mark = time_mark+1
                driver = webdriver.Firefox()
                driver.set_page_load_timeout(10)
                url = 'http://hotel.qunar.com/city/'+str(s)+'/dt-'+str(id)+"/"
                try:
                    driver.get(url)
                except Exception:
                    driver.execute_script("window.stop()")
                sleep(0.5)
                try:
                    driver.find_element_by_id('QunarPopBox') #当出现这个对话框时，页面被锁死，无法点击页面元素，唯有退出
                    driver.delete_all_cookies()
                    driver.close()
                    continue
                except Exception:
                    try:
                        ac = driver.find_element_by_css_selector('a[class="handler js-order-time"]') #先寻找按时间排序按钮，若没有则证明这个酒店没有评论，跳过
                    except Exception:
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'lxml')
                        hotel_name = soup.find_all('div', {'id': 'detail_pageHeader'})[0].find_all('h2')[0].find_all('span')[
                            0].text.replace("'", "\\'")
                        if hotel_name == []: #寻找不到排序按钮，可能是因为页面未加载完（网速慢），有可能是因为没有评论，上面获取hotel_name,如果正常获取，则证明是没有评论
                            driver.close()
                            continue
                        else:
                            sql_commnets = sql_commnets + "('%s','%s','%s','%s')," % (str(id), s, '1991-01-01', '')
                            csv_writer.writerow([str(id), s, '1991-01-01', ''])
                            csv_writer_done.writerow([id, s])
                            print(sql_commnets)
                            driver.close()
                            continue
                    ac.click()
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    try: #分别对应的是只有一页评论和多于一页评论的情况
                        yema_box = soup.find('div',{'class':'js-pager page-cont'}).find_all('a',{'class':'num'})
                        yema = yema_box[-2]['data-pageno']
                    except Exception:
                        yema_box = soup.find('div', {'class': 'js-pager page-cont'}).find_all('span', {'class': 'num'})
                        yema = yema_box[0].text
                    flag = True
                    flag_no_cmt = True
                    for i in range(int(yema)):
                        if flag:
                            soup = BeautifulSoup(driver.page_source,'lxml')
                            comment_list = soup.find('div',{'class':'js-feed-list'}).find_all('div',{'class':'b_ugcfeed clrfix js-feed'})
                            for comment_box in comment_list:
                                daytime = comment_box.find('li',{'class':'item pubdate'}).find('a')['title']+":00"
                                daytime = daytime.replace('日','').replace('月','-').replace('年','-')
                                if daytime.split('-')[1]=='09' and daytime.split('-')[0]=='2017':
                                    flag_no_cmt = False
                                    try:
                                        comment = comment_box.find('p',{'class':'js-full'}).text
                                        pattern = re.compile('[\r\n]+')
                                        comment_clean = pattern.sub('',comment).replace('\'','').replace('\\','')
                                    except Exception:
                                        comment_clean='no comment'
                                    sql_commnets = sql_commnets + "('%s','%s','%s','%s')," % (str(id),s,daytime,comment_clean)
                                    csv_writer.writerow([str(id),s,daytime,comment_clean])
                                elif daytime.split('-')[1]!='09' and daytime.split('-')[1]!='10':
                                    flag=False
                                    break
                            try:
                                page_next = driver.find_element_by_css_selector('div[class="ui-page"]').find_element_by_css_selector('a[class="num icon-tag"]')
                                page_next.click()
                                tim = random.randint(0.5,1)
                                sleep(tim)
                            except Exception:
                                continue
                        else:
                            break
                    if flag_no_cmt==True:
                        sql_commnets = sql_commnets + "('%s','%s','%s','%s')," % (str(id), s, '1991-01-01', '')
                        csv_writer.writerow([str(id), s, '1991-01-01', ''])
                        driver.close()
                    print(sql_commnets[:-1])
                csv_writer_done.writerow([id,s])
                driver.close()
            except Exception  as e:
                print(e)
                try:
                    driver.close()
                except Exception:
                    pass
                continue

if __name__ == '__main__':
    sql = 'select distinct(hotel_id),shi from qnr_hotel_id where shi="foshan"'
    # sql2 = 'select distinct(hotel_id),shi from qnr_hotel_details'
    # cursor.execute(sql)
    # list1 = []
    # for row in cursor.fetchall():
    #     list1.append(list(row))
    # cursor.execute(sql2)
    # list2 = []
    # for row in cursor.fetchall():
    #     list2.append(list(row))
    hotel_list_pd = pd.read_csv('qnr_hotel_details.csv')[['hotel_id','shi']]
    done_pd = done_list_list = pd.read_csv('qnr-done.csv')[['hotel_id','shi']]
    hotel_list = []
    done = []
    for row in hotel_list_pd.itertuples():
        hotel_list.append([row[1],row[2]])
    for row in done_pd.itertuples():
        done.append([row[1],row[2]])
    incre_cmt(hotel_list,done)
