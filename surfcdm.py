from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
import re

# defining headers to avoid 418 error 
h = {'User-Agent': 'Mozilla/5.0'}

# defining the starting url and webpage visit limit
startUrl = 'http://cdm.depaul.edu'
visitLimit = 10000

# initializing a list and dictonary 
visitedUrl = []
wordFrequencies = {}

class WordCounter(HTMLParser):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.links = []                                                   
        self.skipTag = False                                              # intializing a flag to skip certain html tags

    def handle_data(self, data):
        if self.skipTag:                                                  # if skipTag is true then skip processing the text
            return
        words = re.findall(r'\b\w+\b', data)                              # extracting words from the webpage 
        for word in words:
            wordFrequencies[word] = wordFrequencies.get(word, 0) + 1      # counting the number of occurances of each word

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:                                    # skip parsing if it's a script or style tag
            self.skipTag = True
        else:
            self.skipTag = False

        if tag == 'a':                                                    
            for attr in attrs:
                if attr[0] == 'href':                                     # checking for 'href' attribute in attributes 
                    link = urljoin(self.url, attr[1])
                    parsed_url = urlparse(link)
                    if parsed_url.netloc == urlparse(startUrl).netloc and not link.endswith('.pdf'):                   # only crawling CDM webpages 
                        self.links.append(link)

def crawlUrl(url):
    '''
    Analyzes webpages for information 
    '''
    if len(visitedUrl) >= visitLimit:                            # checking if we have reached the maximum limit of webpages
        return
    if url in visitedUrl:                                        # checking if we have already visited the webpage
        return
    
    try:
        visitedUrl.append(url)                                   
        response = urlopen(Request(url, headers=h))
        html = response.read().decode('utf-8')                   # retrieving the data in bytes and then converting it to strings
        parser = WordCounter(url)
        parser.feed(html)                                        # extracting all the information on the website 

        for link in parser.links:                                # parsing through all the links in the webpage 
            crawlUrl(link)                    

    except Exception as e:
        print("Error while crawling", url, e)                    # printing the urls which could not be parsed 

crawlUrl(startUrl)

sortedWordfrequencies = sorted(wordFrequencies.items(), key=lambda x: x[1], reverse=True)                     # storing word-count pairs in descending order 

file = open("crawl_results2.txt", "w")                                      # creating a file to write the results to it

file.write("The 25 most common words on the CDM website:\n")
for word, count in sortedWordfrequencies[:25]:                              # writing the words into the file
    file.write(f"Word: {word}\tCount: {count}\n")

file.close()      
