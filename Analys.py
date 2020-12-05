import PySimpleGUI as sg
import codecs
import os
import sys
import pandas as pd
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

list_1 = []
list_2 = []

def main():
    # Define the window's contents

    state_list=[]
    for folder in os.listdir(os.getcwd()+"/data/"):
        state_list.append(folder)

    first = [[sg.Text("şehir")],
              [sg.Input(key='-CITY-')],
              [sg.Text("mahalle")],
              [sg.Listbox(values=state_list,key='-STATE-')],
              [sg.Text("Yıl")],
              [sg.Input(key='-YEAR-')],
             [sg.Text("Tarih")],
             [sg.Input(key='-DATE-')],
             [sg.Text("Haftasonu")],
             [sg.Input(key='-WEEKEND-')],
              [sg.Text("Hız")],
              [sg.Input(key='-SPEED-')],
              [sg.Text("Servis")],
              [sg.Input(key='-SERVICE-')],
              [sg.Text("Lezzet")],
              [sg.Input(key='-TASTE-')],

              [sg.Button('Ok')],

    ]
    second = [[sg.Text("şehir")],
              [sg.Input(key='-CITY2-')],
              [sg.Text("mahalle")],
              [sg.Listbox(values=state_list,key='-STATE2-')],
              [sg.Text("Yıl")],
              [sg.Input(key='-YEAR2-')],
              [sg.Text("Tarih")],
              [sg.Input(key='-DATE2-')],
              [sg.Text("Haftasonu")],
              [sg.Input(key='-WEEKEND2-')],
              [sg.Text("Hız")],
              [sg.Input(key='-SPEED2-')],
              [sg.Text("Servis")],
              [sg.Input(key='-SERVICE2-')],
              [sg.Text("Lezzet")],
              [sg.Input(key='-TASTE2-')],

              [sg.Button('Ok2')],
]

    layout = [
        [
            sg.Column(first),
            sg.VSeperator(),
            sg.Column(second),
            sg.Button('Karşılaştır'),
            sg.Input(key='-COMPAREDATE-'),
            sg.Button('Günlük')
        ]
        ]



    # Create the window
    window = sg.Window('Window Title', layout)

    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break
        # Output a message to the window


        if event == 'Ok':
            list_1=get_info(
                values['-CITY-'],values['-STATE-'],values['-YEAR-']
                ,values['-SPEED-'],values['-TASTE-'],values['-SERVICE-']
                ,values['-DATE-'],values['-WEEKEND-'],os.getcwd(),'list1'
            )

        if event == 'Ok2':
            list_2=get_info(
                values['-CITY2-'],values['-STATE2-'],values['-YEAR2-']
                ,values['-SPEED2-'],values['-TASTE2-'],values['-SERVICE2-']
                ,values['-DATE2-'],values['-WEEKEND2-'],os.getcwd(),'list2'
            )

        if event=='Karşılaştır':
            compare(list_1,list_2)

        if event=='Günlük':
            daily(list_1,list_2,values['-COMPAREDATE-'])


    # Finish up by removing from the screen
    window.close()

def daily(list_1,list_2,date):

    most_frequent_food_daily={}
    most_frequent_food_daily2={}
    for item in list_1:
        for k in item['yorumlar']:
            if k['tarih']==date:
                for e in k['yorum-yemek']:
                    if e not in most_frequent_food_daily.keys():
                        most_frequent_food_daily[e]=0
                    else:
                        most_frequent_food_daily[e]=most_frequent_food_daily[e]+1


    for item in list_2:
        for k in item['yorumlar']:
            if k['tarih']==date:
                for e in k['yorum-yemek']:
                    if e not in most_frequent_food_daily2.keys():
                        most_frequent_food_daily2[e]=0
                    else:
                        most_frequent_food_daily2[e]=most_frequent_food_daily2[e]+1

    fig, axs = plt.subplots(2, 2)
    axs[0, 0].scatter(most_frequent_food_daily.keys(), most_frequent_food_daily.values())
    axs[0, 0].set_title('1. Bölge' + date)
    axs[0, 1].scatter(most_frequent_food_daily2.keys(), most_frequent_food_daily2.values())
    axs[0, 1].set_title("2.bölge"+ date)
    fig.show()

def compare(list_1,list_2):
    daily_comment_count={}
    monthly_commnet_count={}
    most_frequent_food_daily={}
    most_frequent_food_monthly={}
    daily_comment_count2={}
    monthly_commnet_count2={}
    most_frequent_food_daily2={}
    most_frequent_food_monthly2={}
    i=0
    while i<20:

        daily_comment_count[(datetime.today() - timedelta(days=i)).strftime("%d/%m/%Y")]=0
        i=i+1
    i=0
    while i<12:
        monthly_commnet_count[str(i)]=0
        i=i+1
    i=0
    while i<20:

        daily_comment_count2[(datetime.today() - timedelta(days=i)).strftime("%d/%m/%Y")]=0
        i=i+1
    i=0
    while i<12:
        monthly_commnet_count2[str(i)]=0
        i=i+1

    for item in list_1:
        for k in item['yorumlar']:
            if k['tarih'] in daily_comment_count.keys():

                daily_comment_count[k['tarih']]=daily_comment_count[k['tarih']]+1
                for e in k['yorum-yemek']:
                    if e not in most_frequent_food_daily.keys():

                        most_frequent_food_daily[e]=0
                    else:
                        most_frequent_food_daily[e]=most_frequent_food_daily[e]+1

    for item in list_1:
        for k in item['yorumlar']:
            if k['ay'] in monthly_commnet_count.keys():
                monthly_commnet_count[k['ay']] = monthly_commnet_count[k['ay']] + 1
                for e in k['yorum-yemek']:
                    if e not in most_frequent_food_monthly.keys():
                        most_frequent_food_monthly[e]=0
                    else:
                        most_frequent_food_monthly[e]=most_frequent_food_monthly[e]+1


    for item in list_2:
        for k in item['yorumlar']:
            if k['tarih'] in daily_comment_count2.keys():

                daily_comment_count2[k['tarih']]=daily_comment_count2[k['tarih']]+1
                for e in k['yorum-yemek']:
                    if e not in most_frequent_food_daily2.keys():

                        most_frequent_food_daily2[e]=0
                    else:
                        most_frequent_food_daily2[e]=most_frequent_food_daily2[e]+1

    for item in list_2:
        for k in item['yorumlar']:
            if k['ay'] in monthly_commnet_count2.keys():
                monthly_commnet_count2[k['ay']] = monthly_commnet_count2[k['ay']] + 1
                for e in k['yorum-yemek']:
                    if e not in most_frequent_food_monthly2.keys():
                        most_frequent_food_monthly2[e]=0
                    else:
                        most_frequent_food_monthly2[e]=most_frequent_food_monthly2[e]+1


    print(daily_comment_count)
    print(most_frequent_food_daily)
    print(most_frequent_food_monthly)
    print(monthly_commnet_count)
    print(daily_comment_count2)
    print(most_frequent_food_daily2)
    print(most_frequent_food_monthly2)
    print(monthly_commnet_count2)


    daily_comment_count_list=[]
    for i in daily_comment_count.keys():
        daily_comment_count_list.append(i[0:2])

    daily_comment_count_list2 = []
    for i in daily_comment_count2.keys():
        daily_comment_count_list2.append(i[0:2])

    fig, axs = plt.subplots(2, 4)
    axs[0, 0].scatter(daily_comment_count_list, daily_comment_count.values())
    axs[0, 0].set_title('1. Bölge Günlük yorum sayıları(son 20 gün)')
    axs[0, 1].scatter(monthly_commnet_count.keys(), monthly_commnet_count.values())
    axs[0, 1].set_title('1. Bölge Aylık yorum sayıları(son 12 ay)')
    axs[0, 2].scatter(most_frequent_food_daily.keys(), most_frequent_food_daily.values())
    axs[0, 2].set_title('1. Bölge En çok tercih edilen yemekler(son 20 gün)')
    axs[0, 3].scatter(most_frequent_food_monthly.keys(), most_frequent_food_monthly.values())
    axs[0, 3].set_title('1. Bölge En çok tercih edilen yemekler(son 12 ay)')
    axs[1, 0].scatter(daily_comment_count_list2, daily_comment_count2.values())
    axs[1, 0].set_title('2. Bölge Günlük yorum sayıları(son 20 gün)')
    axs[1, 1].scatter(monthly_commnet_count2.keys(), monthly_commnet_count2.values())
    axs[1, 1].set_title('2. Bölge Aylık yorum sayıları(son 12 ay)')
    axs[1, 2].scatter(most_frequent_food_daily2.keys(), most_frequent_food_daily2.values())
    axs[1, 2].set_title('2. Bölge En çok tercih edilen yemekler(son 20 gün)')
    axs[1, 3].scatter(most_frequent_food_monthly2.keys(), most_frequent_food_monthly2.values())
    axs[1, 3].set_title('2. Bölge En çok tercih edilen yemekler(son 12 ay)')

    fig.show()

def get_info(city,state,year,speed,taste,service,date,weekend,path,name):
    path=path+"/data/"
    speed=speed.split('-')
    taste=taste.split('-')
    service=service.split('-')
    print(speed)
    print(taste)
    print(service)
    print(city)
    print(state)
    print(year)
    list=[]

    path=path+state[0]+"/"


    result=[]

    for file in os.listdir(path):


        try:
            with open(path+"/"+file, 'r', encoding='utf8') as wf:
                data = json.loads(wf.read())

                if data['city'] == city and data['state'] == state[0] \
                        and float(speed[0]) < float(data['Hız'].replace(',', '.')) \
                        and float(speed[1]) > float(data['Hız'].replace(',', '.')) \
                        and float(taste[0]) < float(data['Lezzet'].replace(',', '.')) \
                        and float(taste[1]) > float(data['Lezzet'].replace(',', '.')) \
                        and float(service[0]) < float(data['Servis'].replace(',', '.')) \
                        and float(service[1]) > float(data['Servis'].replace(',', '.')):

                    for item in data['yorumlar']:

                        if date!='' and item['tarih']!=date:
                            data['yorumlar'].remove(item)
                            pass
                        else:
                            if year!='' and item['yıl']!=year:
                                data['yorumlar'].remove(item)
                                pass
                            else:
                                if weekend!='' and item['haftasonu']!=weekend:
                                    data['yorumlar'].remove(item)
                                    pass
                                else:
                                    result.append(data)




        except:
            pass


    return result


if __name__ == "__main__":
    main()