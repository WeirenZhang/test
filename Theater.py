import collections
import json
from urllib import request
from datetime import datetime
import requests
from datetime import datetime,timezone,timedelta

url = 'https://script.google.com/macros/s/AKfycbwwB2Ke85PFeQqt2P9BRZFOxWif6JI4_ImblPyfFlP-VTJLkJJ6sZkCMD4tPhF_g8yT/exec'
area ={1:'臺北', 2:'桃園', 3:'新竹', 4:'臺中', 5:'臺南', 6:'高雄', 7:'屏東', 8:'', 9:'苗栗', 10:'澎湖', 11:'花蓮', 12:'嘉義'}
movie_rating ={0:'https://seo.docs.com.tw/cinema/photo/5140_1.png', 1:'https://seo.docs.com.tw/cinema/photo/5140_2.png', 2:'https://seo.docs.com.tw/cinema/photo/5140_3.png', 3:'https://seo.docs.com.tw/cinema/photo/5140_4.png', 4:'https://seo.docs.com.tw/cinema/photo/5140_5.png'}

dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
dt2 = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區
now_date = dt2.strftime("%Y-%m-%d %H:%M:%S") # 將時間轉換為 string
print(now_date) 

results = []

data = request.urlopen('https://www.ezding.com.tw/new_ezding/cinemas?location=%20&valid=1').read().decode("utf-8")
parsedJson = json.loads(data)

location_list = []
cinemas_list = []
for item in parsedJson['result']:
    Dictionary ={'cinema_id':item['cinema_id'], 'cinema_name':item['cinema_name']['zh_tw'], 'location':item['location'], 'address':item['address'], 'phone':item['phone']}
    location_list.append(item['location'])
    cinemas_list.append(Dictionary)
    
    find_movie_by_cinema_list = []
    response = request.urlopen('https://www.ezding.com.tw/new_ezding/orders/find_movie_by_cinema?cinema_id=' + item['cinema_id'] + '&page=1&page_size=15').read().decode("utf-8")
    data = json.loads(response)   
    if (data['status'] == 'success'):
        if (len(data['result']['list']) > 0):
            for d in data['result']['list']:
                movie_list = []
                for k in d['movie_list']:
                    sdata= []
                    for f in k['sdata']:
                        type_session = []
                        type_session.append({'type':f['movie_version']})
                        data_session= []
                        for f1 in f['data_session']:
                            data_session.append({'time':datetime.fromtimestamp(f1['session_time']/1000).strftime("%H:%M")})
                        Dictionary = {'types':type_session,'times':data_session}
                        sdata.append(Dictionary)

                    Dictionary = {'id':k['movie_id'], 'theaterlist_name':k['movie_title']['zh_tw'], 'en':k['movie_title']['en_us'], 'release_movie_time':'未訂' if (str(k['release_date']) == '0' or k['release_date'] == None) else datetime.fromtimestamp(k['release_date']/1000).strftime("%Y/%m/%d"), 'release_foto':'https://www.ezding.com.tw/static/common/poster.png' if (k['poster_url'] == "" or k['poster_url'] == None) else k['poster_url'], 'icon':movie_rating[k['grade']], 'length':'-分鐘' if (str(k['movie_length']) == '0' or k['movie_length'] == None) else str(k['movie_length'])+'分鐘', 'types':sdata}
                    movie_list.append(Dictionary)
                
                Dictionary ={'date':datetime.fromtimestamp(d['date']/1000).strftime("%Y/%m/%d"),'data':movie_list}
                find_movie_by_cinema_list.append(Dictionary)  

    json_find_movie_by_cinema_list = json.dumps(find_movie_by_cinema_list,ensure_ascii=False)
    results.append({'cinema_id':item['cinema_id'], 'date':now_date, 'data':json_find_movie_by_cinema_list})

for postcode in results:
    json_results = json.dumps(postcode,ensure_ascii=False)
    #print(json_results)
    form_data = {
        'data':json_results,
        'type':'Theater'
    }
    r = requests.post(url, data=form_data)
    print(r.text)

form_data = {
    'type':'TheaterDataClean'
}
r = requests.post(url, data=form_data)
print(r.text)

results = []
new_cinemas_list = []               
date_list_counter = collections.Counter(location_list)
for x in date_list_counter.keys():
    a = []
    for i in cinemas_list:
        if (x == i['location']):
            b ={'id':i['cinema_id'], 'name':i['cinema_name'], 'adds':i['address'], 'tel':i['phone']}
            a.append(b)
    d ={'theater_top':area[x], 'theater_list':a, 'data_area':x}
    new_cinemas_list.append(d)

json_cinemas_list = json.dumps(new_cinemas_list,ensure_ascii=False)
results.append({'date':now_date, 'data':json_cinemas_list})
for postcode in results:
    json_results = json.dumps(postcode,ensure_ascii=False)
    form_data = {
        'data':json_results,
        'type':'Area'
    }
    r = requests.post(url, data=form_data)
    print(r.text)

    


