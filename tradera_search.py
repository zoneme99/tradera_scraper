from bs4 import BeautifulSoup
import requests
import re
import os
from datetime import datetime
import webbrowser


def soup_maker(newurl):
    url = newurl
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    return soup

def next_page(soup, iterator):
    numpages = soup.find("a", {"class": "page-link"}, string=str(iterator))
    return numpages.get("href")

def append_links(soup, pattern, textfilter, list_object):
    links = soup.find_all("a", class_="text-truncate-two-lines")

    prizes = soup.find_all("span", attrs={"data-testid": "price"})
    dates = soup.find_all("span", {"class":["item-card-animate-time ml-auto text-nowrap size-oslo text-gray-600", "text-nowrap pr-1"]})
    for index, link in enumerate(links):
        if textfilter == True:
            textsoup = soup_maker("https://www.tradera.com"+link.get("href"))
            if not text_search(textsoup, inputs[2]):
                continue
        if pattern.match(link.get_text(strip=True)):
            #reformat prize
            string = re.sub('\s+', '',prizes[index].string)
            string = string.replace("kr","")
            prize = int(string)
            if dates[index].string == "Köp nu":
                tmpdate = datetime(1999,6,23)
            else:
                tmpdate = datetime.strptime(dates[index].string, '%d %b %H:%M')
                today = datetime.today()
                tmpdate = tmpdate.replace(year=today.year)
            list_object.append([link.get("title"), prize, tmpdate, "https://www.tradera.com"+link.get("href")])
    return list_object

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


#Section Functions

def gather_inputs():

    print("Welcome to Tradera_Search!")
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

    while True:
        ans = input("Would you like a descriptionfilter, y/n?(default:no, more efficient)")
        if ans == "n" or len(ans) == 0:
            os.system('cls')
            textfilter = False
            break
        elif ans == "y":
            os.system('cls')
            textfilter = True
            break
        else:
            os.system('cls')
            print("Wrong input")
            


    if textfilter == True:
        textpart = input("what should be included in text: ")
        if len(textpart) > 0:
            textpattern = re.compile('.*'+textpart+'.*', re.IGNORECASE)
        else:
            textpattern = re.compile('.*', re.IGNORECASE)
        os.system('cls')
    else:
        textpattern = None

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

    return [urlsearch, titlepattern, textpattern, sortkey, textfilter]

def gather_links(inputs):
    print("Starting Search Process!")

    links = []
    url = "https://www.tradera.com/search?q="+inputs[0]
    soup = soup_maker(url)

    print("On Page 1")
    links = append_links(soup, inputs[1], inputs[4], links)
    page = 2
    while True:
        try:
            print("On Page "+str(page))
            soup = soup_maker("https://www.tradera.com"+next_page(soup, page))
            links = append_links(soup, inputs[1], inputs[4], links)
            page += 1
            print("Total {} Links Found!".format(len(links)))
        except AttributeError:
            break
    links = sort_list(links, inputs[3])
    return links


    outputlinks = []
    data = []
    for index, link in enumerate(links):
        print("filtering link {} out of {}".format(index, len(links)))
        soup = soup_maker("https://www.tradera.com"+link)
        if text_search(soup, inputs[2]):
            outputlinks.append(link)
            include_data(soup, data)

    item_list = bake(outputlinks, data)
    item_list = sort_list(item_list, inputs[3])
    os.system('cls')
    return item_list

def print_output(filtered_links):
    if len(filtered_links) > 0:

        string = ""
        for _ in range(90+12+20):
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

        print(string)

        string = ""
        for _ in range(90+12+20):
            string += "-"
        print(string)

        for index,[name, prize, date, links] in enumerate(filtered_links):
            if date.year == 1999 and date.month == 6 and date.day == 23:
                tmpdate = "BUY NOW"
            else: 
                tmpdate = date
            string = ""
            string += "|"+str(index)+"|"+name+"|"
            length = len(string)
            if length > 90:
                length -= 50 
            for _ in range(90-length):
                string = string+" "

            string = string+"|{:0,} kr|".format(prize)
            length = len(string)
            for _ in range((90+12)-length):
                string = string+" "
            if type(tmpdate) == type("string"):
                string += "|"+tmpdate+"|"
            else:
                string = string+"|{}-{}-{} {}:{}|".format(tmpdate.year,tmpdate.month,tmpdate.day,tmpdate.hour,tmpdate.minute)
            print(string)
    else:
        input("No items found, press enter to continue")

def idle(bool, links):
    if len(links) > 0:
        while True:
            try:
                num = input("Insert assigned number for item to open url, write exit to proceed: ")
                if num == "exit":
                    break
                num = int(num)
                if num > len(links)-1 or num < 0:
                    print("Out of index")
                    continue
            except ValueError:
                print("No valid input, test again")
            
            webbrowser.open(links[num][3])

            
    while True:
        try:
            num = int(input("enter 0 for exit, enter 1 for new search: "))
            if num == 0:
                return not bool
            elif num == 1:
                return bool
            else:
                os.system('cls')
                print("Can only take in 0 or 1")
        except:
            os.system('cls')
            print("stop messing around")

exit = False
while not exit:
    
    inputs = gather_inputs()
    
    links = gather_links(inputs)

    print_output(links)
    
    exit = idle(exit, links)

