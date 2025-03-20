import collections
import json
from urllib import request
from requests_html import HTMLSession
from datetime import datetime
import requests
from datetime import datetime,timezone,timedelta

url = 'https://script.google.com/macros/s/AKfycbwwB2Ke85PFeQqt2P9BRZFOxWif6JI4_ImblPyfFlP-VTJLkJJ6sZkCMD4tPhF_g8yT/exec'
area ={1:'臺北', 2:'桃園', 3:'新竹', 4:'臺中', 5:'臺南', 6:'高雄', 7:'屏東', 8:'', 9:'苗栗', 10:'澎湖', 11:'花蓮', 12:'嘉義'}
movie_rating ={0:'https://seo.docs.com.tw/cinema/photo/5140_1.png', 1:'https://seo.docs.com.tw/cinema/photo/5140_2.png', 2:'https://seo.docs.com.tw/cinema/photo/5140_3.png', 3:'https://seo.docs.com.tw/cinema/photo/5140_4.png', 4:'https://seo.docs.com.tw/cinema/photo/5140_5.png'}
type ={0:'https://www.ezding.com.tw/new_ezding/ranking_list/order_top?page={0}&page_size=12', 1:'https://www.ezding.com.tw/new_ezding/ranking_list/coming?page={0}&page_size=12'}

dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
dt2 = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區
now_date = dt2.strftime("%Y-%m-%d %H:%M:%S") # 將時間轉換為 string
print(now_date) 

results = []
for _type in range(2):
    data = request.urlopen(type[_type].format("1")).read().decode("utf-8")
    parsedJson = json.loads(data)
    total_pages = parsedJson['result']['total_pages']
    #print(total_pages)

    for item in parsedJson['result']['list']:
        # 创建session对象
        session = HTMLSession()
        # 发送GET请求
        response = session.get('https://www.ezding.com.tw/movieInfo?movieid='+ item['movie_id'] +'&tab=0')
        # 解析HTML响应
        title = response.html.xpath('//script[@id="__NEXT_DATA__"]')[0].text
        parsedJson = json.loads(title)
        # 打印标题
        movie_description = parsedJson['props']['pageProps']['info']['movieInfo']['movie_description']

        actor = ''
        director = ''
        movie_staffs = parsedJson['props']['pageProps']['info']['movieInfo']['movie_staff']
        for movie_staff in movie_staffs:
            
            if "2" in movie_staff['staff_type']:
                actor += movie_staff['staff_name'] + '' + '，'
            if "1" in movie_staff['staff_type']:
                director += movie_staff['staff_name']+'，'
        
        params = {
        'fr':'@movies-www',
        'enc':'UTF-8',
        'type':'all',
        'search_term':item['movie_title']['zh_tw']
        }

        referer_session = HTMLSession()
        referer_session.headers.update({'referer': 'http://www.atmovies.com.tw/'})
        response = referer_session.post('http://search.atmovies.com.tw/search/', data=params)
        # 解析HTML响应
        #print(response.text)
        title_list = response.html.xpath('//a[@class="title big"]')
        if (len(title_list) > 0):
            title = title_list[0].attrs["href"].split("/")[-1]
            response = session.get('http://app2.atmovies.com.tw/filmMoreTrailer/' + title + '/')
            title_list = response.html.xpath('//div[@style="margin:10px 0;"]')
            ary = []
            for i in title_list:
                #print(i.text)
                #print(i.find('iframe')[0].attrs["src"])
                Dictionary ={'title':i.text, 'href':i.find('iframe')[0].attrs["src"], 'cover':'https://img.youtube.com/vi/' + i.find('iframe')[0].attrs["src"].split("/")[-1] + '/sddefault.jpg'}
                ary.append(Dictionary)
            json_video = json.dumps(ary,ensure_ascii=False)
        else:
            title = ''
            ary = []
            json_video = json.dumps(ary,ensure_ascii=False)

        list = []
        for i in range(12):
            i+=1
            response = request.urlopen('https://www.ezding.com.tw/new_ezding/orders/find_location_cinema?movie_id='+ item['movie_id'] +'&location='+ str(i) +'&page=1&page_size=200').read().decode("utf-8")
            data = json.loads(response)   
            if (data['status'] == 'success'):
                if (len(data['result']['list']) > 0):
                    for d in data['result']['list']:
                        sdata = []
                        for k in d['sdata']:
                            type_session = []
                            type_session.append({'type':k['movie_version']})
                            data_session = []
                            for f in k['data_session']:
                                data_session.append({'time':datetime.fromtimestamp(f['session_time']/1000).strftime("%H:%M")})
                            Dictionary ={'types':type_session, 'id':k['cinema_data']['cinema_id'], 'theater':k['cinema_data']['cinema_name']['zh_tw'],'times':data_session}
                            sdata.append(Dictionary)
                            
                        Dictionary ={'area':area[i], 'date':datetime.fromtimestamp(d['date']/1000).strftime("%Y/%m/%d"),'data':sdata}
                        list.append(Dictionary)  
                        
        new_list = []
        date_list = []
        for i in list:
            date_list.append(i['date'])
        date_list_counter = collections.Counter(date_list)
        for x in date_list_counter.keys():
            a = []
            for i in list:
                if (x == i['date']):
                    b ={'area':i['area'], 'data':i['data']}
                    a.append(b)
            d ={'date':x, 'list':a}
            new_list.append(d)

        for i in new_list:
            for j in i['list']:
                cinema_id_list = []
                for k in j['data']:
                    cinema_id_list.append(k['id'] + '&' + k['theater'])
                cinema_id_list_counter = collections.Counter(cinema_id_list)
                #print(i['date'])
                #print(cinema_id_list_counter)
                e = []
                for x in cinema_id_list_counter.keys():
                    a = []
                    for k in j['data']:
                        if (x.split("&")[0] == k['id']):
                            b ={'types':k['types'], 'times':k['times']}
                            a.append(b)
                    d ={'id':x.split("&")[0], 'theater':x.split("&")[-1], 'types':a}
                    e.append(d)
                #print(e)
                j['data'] = e

        json_data = json.dumps(new_list,ensure_ascii=False)
        #print(json_data)

        dict = {'type':_type, 'date':now_date, 'page':'1', 'zh_tw':item['movie_title']['zh_tw'], 'en_us':item['movie_title']['en_us'], 'release_date':datetime.fromtimestamp(item['release_date']/1000).strftime("%Y/%m/%d"), 'poster_url':'https://www.ezding.com.tw/static/common/poster.png' if (item['poster_url'] == "" or item['poster_url'] == None) else item['poster_url'], 'movie_id':item['movie_id'], 'movie_length':'-分鐘' if (str(item['movie_length']) == '0' or item['movie_length'] == None) else str(item['movie_length'])+'分鐘', 'grade':movie_rating[item['grade']], 'movie_description':movie_description, 'director':director[:-1], 'actor':actor[:-1], 'filmMoreTrailer':json_video, 'find_location_cinema':json_data}
        results.append(dict)

    count = 2
    while (count <= total_pages ):
        data = request.urlopen(type[_type].format(str(count))).read().decode("utf-8")
        parsedJson = json.loads(data)
        for item in parsedJson['result']['list']:
            # 创建session对象
            session = HTMLSession()
            # 发送GET请求
            response = session.get('https://www.ezding.com.tw/movieInfo?movieid='+ item['movie_id'] +'&tab=0')
            # 解析HTML响应
            title = response.html.xpath('//script[@id="__NEXT_DATA__"]')[0].text
            parsedJson = json.loads(title)
            # 打印标题
            movie_description = parsedJson['props']['pageProps']['info']['movieInfo']['movie_description']

            actor = ''
            director = ''
            movie_staffs = parsedJson['props']['pageProps']['info']['movieInfo']['movie_staff']
            for movie_staff in movie_staffs:
                if "2" in movie_staff['staff_type']:
                    actor += movie_staff['staff_name']+'，'
                if "1" in movie_staff['staff_type']:
                    director += movie_staff['staff_name']+'，'

            params = {
            'fr':'@movies-www',
            'enc':'UTF-8',
            'type':'all',
            'search_term':item['movie_title']['zh_tw']
            }

            referer_session = HTMLSession()
            referer_session.headers.update({'referer': 'http://www.atmovies.com.tw/'})
            response = referer_session.post('http://search.atmovies.com.tw/search/', data=params)
            # 解析HTML响应
            title_list = response.html.xpath('//a[@class="title big"]')
            if (len(title_list) > 0):
                title = title_list[0].attrs["href"].split("/")[-1]
                response = session.get('http://app2.atmovies.com.tw/filmMoreTrailer/' + title + '/')
                title_list = response.html.xpath('//div[@style="margin:10px 0;"]')
                ary = []
                for i in title_list:
                    #print(i.text)
                    #print(i.find('iframe')[0].attrs["src"])
                    Dictionary ={'title':i.text, 'href':i.find('iframe')[0].attrs["src"], 'cover':'https://img.youtube.com/vi/' + i.find('iframe')[0].attrs["src"].split("/")[-1] + '/sddefault.jpg'}
                    ary.append(Dictionary)
                json_video = json.dumps(ary,ensure_ascii=False)
            else:
                title = ''
                ary = []
                json_video = json.dumps(ary,ensure_ascii=False)

            list = []
            for i in range(12):
                i+=1
                #print('https://www.ezding.com.tw/new_ezding/orders/find_location_cinema?movie_id='+ item['movie_id'] +'&location='+ str(i) +'&page=1&page_size=200')
                response = request.urlopen('https://www.ezding.com.tw/new_ezding/orders/find_location_cinema?movie_id='+ item['movie_id'] +'&location='+ str(i) +'&page=1&page_size=200').read().decode("utf-8")
                data = json.loads(response)   
                if (data['status'] == 'success'):
                    if (len(data['result']['list']) > 0):
                        for d in data['result']['list']:
                            sdata = []
                            for k in d['sdata']:
                                type_session = []
                                type_session.append({'type':k['movie_version']})
                                data_session = []
                                for f in k['data_session']:
                                    data_session.append({'time':datetime.fromtimestamp(f['session_time']/1000).strftime("%H:%M")})
                                Dictionary ={'types':type_session, 'id':k['cinema_data']['cinema_id'], 'theater':k['cinema_data']['cinema_name']['zh_tw'],'times':data_session}
                                sdata.append(Dictionary)
                            
                            Dictionary ={'area':area[i], 'date':datetime.fromtimestamp(d['date']/1000).strftime("%Y/%m/%d"),'data':sdata}
                            list.append(Dictionary)  
                        
            new_list = []
            date_list = []
            for i in list:
                date_list.append(i['date'])
            date_list_counter = collections.Counter(date_list)
            for x in date_list_counter.keys():
                a = []
                for i in list:
                    if (x == i['date']):
                        b ={'area':i['area'], 'data':i['data']}
                        a.append(b)
                d ={'date':x, 'list':a}
                new_list.append(d)

            for i in new_list:
                for j in i['list']:
                    cinema_id_list = []
                    for k in j['data']:
                        cinema_id_list.append(k['id'] + '&' + k['theater'])
                    cinema_id_list_counter = collections.Counter(cinema_id_list)
                    #print(i['date'])
                    #print(cinema_id_list_counter)
                    e = []
                    for x in cinema_id_list_counter.keys():
                        a = []
                        for k in j['data']:
                            if (x.split("&")[0] == k['id']):
                                b ={'types':k['types'], 'times':k['times']}
                                a.append(b)
                        d ={'id':x.split("&")[0], 'theater':x.split("&")[-1], 'types':a}
                        e.append(d)
                    #print(e)
                    j['data'] = e
            
            json_data = json.dumps(new_list,ensure_ascii=False)
            #print(json_data)

            dict = {'type':_type, 'date':now_date, 'page':str(count), 'zh_tw':item['movie_title']['zh_tw'], 'en_us':item['movie_title']['en_us'], 'release_date':datetime.fromtimestamp(item['release_date']/1000).strftime("%Y/%m/%d"), 'poster_url':'https://www.ezding.com.tw/static/common/poster.png' if (item['poster_url'] == "" or item['poster_url'] == None) else item['poster_url'], 'movie_id':item['movie_id'], 'movie_length':'-分鐘' if (str(item['movie_length']) == '0' or item['movie_length'] == None) else str(item['movie_length'])+'分鐘', 'grade':movie_rating[item['grade']], 'movie_description':movie_description, 'director':director[:-1], 'actor':actor[:-1], 'filmMoreTrailer':json_video, 'find_location_cinema':json_data}
            results.append(dict)
        count+=1
    _type+=1

for postcode in results:
    #print(postcode['page'])
    #print('\n')
    json_results = json.dumps(postcode,ensure_ascii=False)
    form_data = {
        'data':json_results,
        'type':'Movie'
    }
    r = requests.post(url, data=form_data)
    print(r.text)

form_data = {
    'type':'MovieDataClean'
}
r = requests.post(url, data=form_data)
print(r.text)
    
    


