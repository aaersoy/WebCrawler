from datetime import datetime
from time import sleep
import requests
from satl import Satl
from bs4 import BeautifulSoup
import re
import json
import sys
import os
import codecs

from datetime import datetime, timedelta
from utils.printer import printer

base_url = 'https://www.yemeksepeti.com'
restaurant_url = base_url + '/%s/%s'
top_restaurants_url = base_url + '/Restaurants-%s-%sActivities-%s.html'


def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'
    }
    printer('blue', 'Get', url)
    try:
        html = requests.get(url, headers=headers)
    except:
        pass
    sleep(1)
    soup = BeautifulSoup(html.content, 'html.parser')
    return soup


def get_images(satl_obj):
    count = satl_obj.count_files()
    if count != 0:
        return False
    index = 1
    for url in satl_obj.get('images'):
        printer('cyan', 'Download', url)
        try:
            img = requests.get(url)
            satl_obj.attach_file_object(img.content, '%s.jpg' % index)
        except:
            pass
        index += 1
    return True


def crawl_restaurant(keys, response):
    page = get_page(keys)

    """CRAWL RESTAURANT RATIO"""
    try:
        ratios = page.find_all('div', class_='detailArea resPoints')
        elements_with_class = []

        for item in ratios:
            elements_with_class = item.find_all('span', class_='point')
            try:
                response['Hız'] = elements_with_class[0].get_text()
                response['Servis'] = elements_with_class[1].get_text()
                response['Lezzet'] = elements_with_class[2].get_text()
            except:

                response['Hız'] = 'Vale'
                response['Servis'] = elements_with_class[0].get_text()
                response['Lezzet'] = elements_with_class[1].get_text()
    except:
        response['Hız'] = ''
        response['Servis'] = ''
        response['Lezzet'] = ''
    return response


def crawl_restaurant_menu(keys, response):
    """CRAWL RESTAURANT MENU"""
    page = get_page(keys)
    try:
        menu = page.find('div', id='restaurant_menu').find_all('div', class_='restaurantDetailBox None')

        response['menu'] = {}

        for item in menu:
            items_li = item.find('div', class_='listBody').find('ul')
            price = 0

            for e in items_li:
                # print(e)
                try:
                    product = e.find('div', class_='product').find('div', class_='product-info').find('a').get_text()
                    price = e.find('div', class_='product-price').find('span', class_='price').get_text()
                    response['menu'][product] = price
                except:
                    continue
    except:
        response['menu'] = {}
    finally:
        return response


def crawl_restaurant_service_area(keys, response):
    """CRAWL RESTAURANT SERVICE AREA"""
    page = get_page(keys)
    response['servis-alani'] = []
    try:
        info = page.find('div', id='restaurant_info') \
            .find('div', class_='row orderDetails') \
            .find('div', class_='col-16-3 deliveryRegions') \
            .find('div', id='popup1') \
            .find('div', class_='ys-panel ys-tabs ys-restaurantDetails restaurant-properties') \
            .find('div', class_='panel-body') \
            .find('div', id='regions').find_all('div', class_='ys-po-item')

        for item in info:
            list_area = item.find('div', class_='actions').find_all('a')
            for e in list_area:
                response['servis-alani'].append(e.get_text())
    except:
        response['servis-alani'] = {}
    finally:
        return response


def dates_of_comments(date_coef, date_in_comment, storage):
    print(type(date_coef))
    print(type(date_in_comment))
    storage['tarih'] = (datetime.today() - timedelta(days=date_in_comment * date_coef)).strftime("%d/%m/%Y")
    storage['ay'] = (datetime.today() - timedelta(days=date_in_comment * date_coef)).strftime("%m")
    storage['yıl'] = (datetime.today() - timedelta(days=date_in_comment * date_coef)).strftime("%y")
    if (datetime.today() - timedelta(days=date_in_comment * date_coef)).strftime("%A") == 'Saturaday' \
            or (datetime.today() - timedelta(days=date_in_comment * date_coef)).strftime("%A") == 'Sunday':
        storage['haftasonu'] = 'True'
    else:
        storage['haftasonu'] = 'False'

    if storage['ay'][0] == '0':
        storage['ay'] = storage['ay'][1]

    return storage


def crawl_restaurant_comments(keys, response):
    """CRAWL COMMENTS"""
    page = get_page(keys)

    comments = page.find('div', id='restaurant_comments') \
        .find('div', class_='comments allCommentsArea') \
        .find_all('div', class_='comments-body')

    for item in comments:

            dict = {}
            list_attr_comment = []
            elements = item.find('div', class_='user').find('div', class_='row')\
                .find('div', class_='restaurantPoints col-md-12').find_all('div')
            for e in elements:
                list_attr_comment.append(e.get_text())

            dict['puan'] = list_attr_comment

            str = item \
                .find('div', class_='user').find('div', class_='row') \
                .find('div', class_='commentDate pull-right col-md-4').find('div').get_text()


            if str == 'bugün':
                dict = dates_of_comments(date_coef=0, date_in_comment=0, storage=dict)

            elif str.endswith(' gün önce'):
                if len(str) - len(' gün önce') == 1:
                    dict = dates_of_comments(date_coef=1, date_in_comment=int(str[0]), storage=dict)
                else:
                    dict = dates_of_comments(date_coef=1, date_in_comment=int(str[0:2]), storage=dict)

            elif str.endswith(' ay önce'):
                if len(str) - len(' ay önce') == 1:
                    dict = dates_of_comments(date_coef=30, date_in_comment=int(str[0]), storage=dict)
                else:
                    dict = dates_of_comments(date_coef=30, date_in_comment=int(str[0:2]), storage=dict)
            else:
                dict = dates_of_comments(date_coef=365, date_in_comment=int(str[0:2]), storage=dict)

            print(dict)
            dict['yorum'] = item.find('div', class_='user').find('div', class_='comment row').find('p').get_text()

            response['yorumlar'].append(dict)




    return response


def crawl_restaurant_comments_pages(keys, response):
    page = get_page(keys)
    response['yorumlar'] = []
    try:
        comments = page.find('div', id='restaurant_comments') \
            .find('nav', class_='ys-pagination') \
            .find('ul') \
            .find_all('li')

        for item in comments:
            response = crawl_restaurant_comments("https://www.yemeksepeti.com" + item.find('a').get('href'), response)
    except:
        pass
    finally:
        return response


def crawl_restaurant_content(keys, response):
    """CRAWL RESTAURANT CONTENT"""
    page = get_page(keys)
    response['içerik'] = []

    try:
        titles = page.find('div', id='restaurant_titles').find('div', class_='restaurantsMenu row') \
            .find('ul', class_='twoColumn').find_all('li')

        for item in titles:
            splited = item.find('a').get_text()
            items = splited.split('&')
            for i in items:
                if i.endswith('ler') or i.endswith('lar'):
                    response['içerik'].append(i[0:len(splited) - 3].replace(' ', ''))
                else:
                    response['içerik'].append(i.replace(' ', ''))
    except:
        pass
    finally:
        return response


def get_detail_of_restaurant(keys, response):
    response1 = crawl_restaurant(keys, response)
    response1 = crawl_restaurant_menu(keys, response1)
    response1 = crawl_restaurant_service_area(keys, response1)
    response1 = crawl_restaurant_comments_pages(keys, response1)
    response1 = crawl_restaurant_content(keys, response1)
    return response1


def get_restaurants(keys):
    url = restaurant_url % (keys['city'], keys['state'])
    page = get_page(url)
    restaurants_div = page.find_all('div', class_='ys-item')

    items = []

    for element in restaurants_div:
        items.append({'index': base_url + element.find('a').get('href'),
                      'city': keys['city'],
                      'state': keys['state'],
                      'restaurant_name': element.find('a').get_text()})

    return items


def set_comment_to_meal(response):
    i = 0;

    for comment in response['yorumlar']:
        response['yorumlar'][i]['yorum-yemek'] = []
        str = comment['yorum'].lower().replace(' ', '')
        for item in response['içerik']:
            if item.lower().replace(' ', '') in str:
                response['yorumlar'][i]['yorum-yemek'].append(item)

        for ite in response['menu'].keys():
            if ite.lower().replace(' ', '') in str and ite != '  ':
                if ite not in response['yorumlar'][i]['yorum-yemek']:
                    response['yorumlar'][i]['yorum-yemek'].append(ite)
                    response['içerik'].append(ite)

        i = i + 1
    return response


def is_exists(url):
    return Satl.is_exists(url)


def set_data(data):
    # if is_exists(data['url']):
    #     return False
    data['create_date'] = datetime.now()
    data['updated'] = False
    satl = Satl(data['url'], data=data)
    printer('magenta', 'Save', " %s - %s" % (satl.pk, satl.get('name')))
    satl.save()
    get_images(satl)

    # this part writen beacuse of update images
    # else:
    #     satl = Satl(data['url']).load()
    return False


def save_to_local(response):
    """SAVE TO RESPONSE LOCAL"""

    if (not os.path.exists(sys.path[1] + "/data")):
        os.mkdir(sys.path[1] + "/data")
    if (not os.path.exists(sys.path[1] + "/data/" + response['state'])):
        os.mkdir(sys.path[1] + "/data/" + response['state'])

    with codecs.open(sys.path[1] + "/data/" + response['state'] + '/' + response['name'][28:len(response['name']) - 1]
            .strip().strip('.,') + '.json', 'w', encoding='utf8') as wf:
        json.dump(response, wf, ensure_ascii=False)

    with open(sys.path[1] + "/check_file.txt", 'a+') as fp:
        fp.write(response['name'].strip(' ') + "\n")
        fp.close()


def main():
    addresses = [{'city': 'antalya', 'state': 'aksu-altintas-mah'}]

    restaurants = []

    for address in addresses:
        restaurants += get_restaurants(address)

    checked = []

    with open(sys.path[1] + "/check_file.txt", 'r') as fp:
        for x in fp:
            checked.append(x[0:len(x) - 1])
        fp.close()

    for item in restaurants:
        response = {
            'name': item['index'],
            'city': item['city'],
            'restaurant_name': item['restaurant_name'],
            'state': item['state']
        }

        if response['name'].strip(' ') not in checked:
            response_ret = get_detail_of_restaurant(item['index'], response)
            response_ret = set_comment_to_meal(response_ret)
            save_to_local(response_ret)
        else:
            with open(os.getcwd() + '/data/' + response['state'] + "/" + response['name'][
                                                                         28:len(response['name']) - 1] + ".json", 'r',
                      encoding='utf8') as wf:
                data = json.loads(wf.read())
            response_ret = crawl_restaurant_comments(data['name'] + '?section=comments&page=1', data)
            response_ret = set_comment_to_meal(response_ret)
            save_to_local(response_ret)

    return


if __name__ == "__main__":
    main()
