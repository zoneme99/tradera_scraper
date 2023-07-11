from bs4 import BeautifulSoup
import requests
import re


def soup_maker(newurl):
    url = newurl
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    return soup

def next_page(soup, iterator):
    numpages = soup.find("a", {"class": "page-link"}, string=str(iterator))
    return numpages.get("href")

def append_links(soup, pattern, list_object):
    links = soup.find_all("a")
    if pattern is not None:
        for x in links:
            if pattern.match(x.get_text(strip=True)):
                list_object.append(x.get("href"))
    else:      
        for x in links:
                list_object.append(x.get("href"))


def text_search(soup, pattern):
    box = soup.find(class_="text-inter text-hyphenate undefined")
    if pattern is not None:
        if pattern.match(box.get_text(strip=True)):
            return True
        else:
            return False
    else:
        return True

while True:
    urlsearch = input("What do you search for: ")
    if len(urlsearch) > 0:
        break
    print("Can't be empty, search!")

titlepart = input("what should be included in title: ")
if len(titlepart) > 0:
    titlepattern = re.compile('.*'+titlepart+'.*', re.IGNORECASE)
else:
    titlepattern = None

textpart = input("what should be included in text: ")
if len(textpart) > 0:
    textpattern = re.compile('.*'+textpart+'.*', re.IGNORECASE)
else:
    textpattern = None


links = []
outputlinks = []
url = "https://www.tradera.com/search?q="+urlsearch
soup = soup_maker(url)

append_links(soup, titlepattern, links)
page = 2
while True:
    try:
        soup = soup_maker("https://www.tradera.com"+next_page(soup, page))
        append_links(soup, titlepattern, links)
        page += 1
        print(len(links))
    except AttributeError:
        break

for link in links:
    print("iterating")
    soup = soup_maker("https://www.tradera.com"+link)
    if text_search(soup, textpattern):
        outputlinks.append(link)

if len(outputlinks) > 0:
    for link in outputlinks:
        print("https://www.tradera.com"+link)
