from bs4 import BeautifulSoup
import requests
import re
import os
from datetime import datetime

def soup_maker(newurl):
    url = newurl
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    return soup

def next_page(soup, iterator):
    numpages = soup.find("a", {"class": "page-link"}, string=str(iterator))
    return numpages.get("href")

def append_links(soup, pattern, list_object):
    links = soup.find_all("a", class_="text-truncate-two-lines")
    for x in links:
        if pattern.match(x.get_text(strip=True)):
            list_object.append(x.get("href"))


def text_search(soup, pattern):
    box = soup.find(class_="text-inter text-hyphenate undefined")
    if pattern.match(box.get_text(strip=True)):
        return True
    else:
        return False
    
def include_data(soup, list_object):

    box = soup.find("h1", id="view-item-main")
    itemname = box.get_text(strip=True)
    
    if soup.find("span", class_="bid-details-amount") is None:
        box = soup.find("span", class_="animate-on-value-change_animate-on-value-change__sG4yu")
    else:
        box = soup.find("span", class_="bid-details-amount")
    string = re.sub('\s+', '',box.string)
    string = string.replace("kr","")
    prize = int(string)

    if soup.find("p",class_="bid-details-time-title") is not None:
        box = soup.find("p",class_="bid-details-time-title")
        string = box.get_text(strip=True).replace("Avslutas", "")
        dateobj = datetime.strptime(string, '%d %b %H:%M')
        dateobj = dateobj.replace(year=datetime.today().year)
    else:
        dateobj = datetime(1999,6,23)
    
    list_object.append([itemname, prize, dateobj])
    
def bake(links, data):
    baked_list = []
    for index, [name, prize, date] in enumerate(data):

        baked_list.append([name, prize, date, "https://www.tradera.com"+links[index]])
    return baked_list

def sort_list(list, sortkey):
    if sortkey == 0: #Relevans
        return list
    elif sortkey == 1: #Billigast
        return sorted(list,key=lambda l:l[1])
    elif sortkey == 2: #Går snart ut
        return sorted(list,key=lambda l:l[2])
    else:
        raise ValueError("sortkey out of range")



exit = False

while not exit:
    links = []
    outputlinks = []
    data = []
    print("Welcome to Tradera_Search!")
    print("Beware that if you leave title empty it can increase search time(if what you search for got many pages)")
    while True:
        urlsearch = input("What do you search for: ")
        if len(urlsearch) > 0:
            break
        os.system('cls')
        print("Can't be empty, search!")
    os.system('cls')

    titlepart = input("what should be included in title: ")
    if len(titlepart) > 0:
        titlepattern = re.compile('.*'+titlepart+'.*', re.IGNORECASE)
    else:
        titlepattern = re.compile('.*', re.IGNORECASE)
    os.system('cls')

    textpart = input("what should be included in text: ")
    if len(textpart) > 0:
        textpattern = re.compile('.*'+textpart+'.*', re.IGNORECASE)
    else:
        textpattern = re.compile('.*', re.IGNORECASE)
    os.system('cls')
    
    while True:
        while True:
            try:
                sortkey = int(input("How will it get sorted(assign number), 0:relevance, 1:cheapest, 2:date closure :"))
                break
            except ValueError:
                os.system('cls')
                print("You can only put in a number from 0-2")
        if sortkey == 0 or sortkey == 1 or sortkey == 2:
            break
        else:
            os.system('cls')
            print("Wrong input! Just one number between 0-2")
    
    print("Starting Search Process!")

    url = "https://www.tradera.com/search?q="+urlsearch
    soup = soup_maker(url)

    append_links(soup, titlepattern, links)
    page = 2
    while True:
        try:
            soup = soup_maker("https://www.tradera.com"+next_page(soup, page))
            append_links(soup, titlepattern, links)
            print("On Page "+str(page))
            page += 1
        except AttributeError:
            break
    print("Found {} Links!".format(len(links)))

    for index, link in enumerate(links):
        print("filtering link {} out of {}".format(index, len(links)))
        soup = soup_maker("https://www.tradera.com"+link)
        if text_search(soup, textpattern):
            outputlinks.append(link)
            include_data(soup, data)

    item_list = bake(outputlinks, data)
    item_list = sort_list(item_list, sortkey)
    os.system('cls')
    
    if len(outputlinks) > 0:

        string = ""
        for _ in range(90+12+30+100):
            string += "-"
        print(string)
        
        string = "|TITLAR|"
        length = len(string)
        for _ in range(90-length):
            string = string+" "
        string += "|PRIS|"
        length = len(string)
        for _ in range((90+12)-length):
                string = string+" "
        string += "|SLUTDATUM|"
        length = len(string)
        for _ in range((90+12+30)-length):
                string = string+" "
        string += "|LÄNK|"
        print(string)

        string = ""
        for _ in range(90+12+30+100):
            string += "-"
        print(string)

        for name, prize, date, links in item_list:
            if date.year == 1999 and date.month == 6 and date.day == 23:
                tmpdate = "BUY NOW"
            else: 
                tmpdate = date
            string = ""
            string = string+"|"+name+"|"
            length = len(string)
            if length > 90:
                length -= 50 
            for _ in range(90-length):
                string = string+" "

            string = string+"|{:0,} kr|".format(prize)
            length = len(string)
            for _ in range((90+12)-length):
                string = string+" "
            
            string = string+"|{}|".format(tmpdate)
            length = len(string)
            for _ in range((90+12+30)-length):
                string = string+" "
            
            string = string+"|{}|".format(links)
            print(string)
    else:
        input("No items found, press enter to continue")
    
    while True:
        try:
            num = int(input("enter 0 for exit, enter 1 for new search: "))
            if num == 0:
                exit = not exit
                break
            elif num == 1:
                break
            else:
                os.system('cls')
                print("Can only take in 0 or 1")
        except:
            os.system('cls')
            print("stop messing around")