import time
import csv
from tkinter import scrolledtext
import tkinter as tk
from selenium import webdriver
import json
import pandas as pd
from tkinter import *
import threading

counter = 1
with open('data.txt') as json_file:
    counter = json.load(json_file)
links = []
DicList = []  # list for BBC news
FlyList = []  # list for flights
# 2 drivers for 2 threads for search and save
driver = webdriver.Chrome(r'C:\Users\asafl\PycharmProjects\WebCorowler\chromedriver.exe')
driverBBC = webdriver.Chrome(r'C:\Users\asafl\PycharmProjects\WebCorowler\chromedriver.exe')
# load data from csv file of BBC
with open('BBC.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=';')
    for row in readCSV:
        try:

            DicList.append({1: row[0], 2: row[1], 3: row[2]})
            print("-------------------------------------------")



        except:
            print('csv bad line is empty')
# GUI
window = Tk()

window.title("BBC IAA BotCamp")
window.geometry('700x800')
txt_ = Entry(window, width=30)
txt_.grid(column=1, row=0)

txt = scrolledtext.ScrolledText(window, width=75, height=40)
txt.grid(column=1, row=3)


def IAAsearch():
    driver.get('https://www.iaa.gov.il/he-IL/airports/BenGurion/Pages/OnlineFlights.aspx#')
    stop = 0
    try:
        timeElapse = driver.find_element_by_id('ctl00_rptIncomingFlights_ctl00_pInformationStatusMessage')
    except:
        print('time for reload err')
    print(timeElapse.text[-5:])
    Timepd = pd.to_datetime(timeElapse.text[-5:], format='%H:%M')
    print(Timepd)
    time.sleep(3)
    while stop == 0:
        try:
            eleClick = driver.find_element_by_id('ctl00_rptPaging_ctl06_aNext')
            TRelems = driver.find_elements_by_tag_name('tr')
            for tritem in TRelems:
                minilist = []
                tdelems = tritem.find_elements_by_tag_name('td')
                for tditem in tdelems:
                    if tditem.text != '':
                        minilist.append(tditem.text)

                    print(tditem.text)
                if minilist:
                    FlyList.append(list(minilist))
            for p in FlyList:
                print(p)

            eleClick.click()
            time.sleep(2)
        except:
            print('scanning flights IAA finished')
            stop = 1
    counter = 1
    with open('data.txt') as json_file:
        counter = json.load(json_file)
    counter += 1
    with open('jsons/data' + str(counter) + '.txt', 'w') as outfile:
        json.dump(FlyList, outfile)
    with open('data.txt', 'w') as outfile:
        json.dump(counter, outfile)
    canScanAgain = 0
    while canScanAgain == 0:
        if Timepd + pd.datetime(minute=5) < pd.datetime.now(): # check if 5 minutes paa
            canScanAgain = 1
        else:
            time.sleep(30)
    IAAsearch()


# Start scan IAA site endless loop
x = threading.Thread(target=IAAsearch)
x.start()


def search_for_keywords(keywords, data):
    returnList = []
    for Items in data:
        once = 1
        if keywords in Items[1]:
            txt.insert(tk.END, "---BBC---------------------------------------------------------------------" + '\n')
            txt.insert(tk.END, Items[2] + '\n')
            txt.insert(tk.END, Items[1] + '\n')
            txt.insert(tk.END, Items[3] + '\n')
            once = 2
        if keywords in Items[3] and once == 1:
            txt.insert(tk.END, "---BBC---------------------------------------------------------------------" + '\n')
            txt.insert(tk.END, Items[2] + '\n')
            txt.insert(tk.END, Items[1] + '\n')
            txt.insert(tk.END, Items[3] + '\n')


def SearchBtnClick():
    txt.delete('1.0', END)
    with open('data.txt') as json_file:
        counter_ = json.load(json_file)

    while counter_ >= 2:
        with open('jsons/data' + str(counter_) + '.txt') as json_file:
            loadList = json.load(json_file)
        for load in loadList:
            if txt_.get() in load:
                txt.insert(tk.END, "---IAA---------------------------------------------------------------------" + '\n')
                for l in load:
                    txt.insert(tk.END, l + '\n')

        counter_ -= 1
    search_for_keywords(txt_.get(), DicList)


def BBCsearch():
    driverBBC.get('https://www.bbc.com/')
    media_list = driverBBC.find_elements_by_class_name('block-link__overlay-link')
    for item in media_list:
        text = item.text
        h = item.get_attribute("href")
        if text == '':
            text = h[:-20]
        links.append({1: h, 2: text})

        print(text)
        print(h)

    print("------------------------------------------------------------------------")
    count = 0
    for item in links:
        if count == 2:
            break
        count += 1
        print(item)
        try:
            driverBBC.get(item[1])
            paragrhs = driverBBC.find_elements_by_tag_name('p')
            strs = ''
            for p in paragrhs:
                try:
                    strs += p.text
                except:
                    continue
            flag = 1
            for it in DicList:
                if it[1] == item[2]:
                    flag = 0
            # if item[2] not in DicList:
            if flag == 1:
                DicList.append({1: item[2], 2: item[1], 3: strs})
        except:
            print('not a link')
        time.sleep(1)
    with open('BBC.csv', 'w') as writeFile:
        writer = csv.writer(writeFile, delimiter=';')
        for item in DicList:
            print(item)

            writer.writerow((item[1], item[2], item[3]))


def btnClickBBC():
    x = threading.Thread(target=BBCsearch)
    x.start()


btn = Button(window, text="Search", command=SearchBtnClick)
btn.grid(column=1, row=2)

btn = Button(window, text="BBC", command=btnClickBBC)
btn.grid(column=1, row=4)

window.mainloop()
