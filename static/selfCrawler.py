import requests, time, sqlite3, re
import extractor as xtract
import fileData as p
from urllib.parse import urlparse
CrawlerName = ""

#checks that the url is not one of these file formats, more formats may be added as I find incompatible ones
def fileChecker(url):
    good = True
    badExtensions = ["\.css","\.ico","\.png","\.pdf","\.svg","\.doc","\.docs","\.ppt","\.json"]
    for ext in badExtensions:
        reg = ext + "$"
        if re.search(reg, url):
            good = False
            break
    return good

#checks that the url is correctly formatted
def check(url):
    url_ = url
    p = urlparse(url)
    if re.match(p.netloc+"$",url) and not re.match("/$", url):
        url += "/"
    if re.match("^http://", url) and not re.match("^https?://www.", url):
        url_ = url.replace("http://","https://www.")
    elif re.match("^https://", url) and not re.match("^https?://www.", url):
        url_ = url.replace("https://","https://www.")
    elif not re.match("^https?://", url):
        url_ = "https://"+url
    
    return url_


#Will check the robots.txt file of the site and figure out where it is disallowed
#I learned that urllib had a robots parser afterwards and will eventually
#replace it with that
def checkPermissions(url):
    url = check(url)
    disallowed = []
    #check robots.txt
    robots = requests.get((url+"/robots.txt")).raw
    robots = str(robots).split("/n")
    me = False
    for line in robots:
        x = line.split(":")
        if x[0] == "User-agent":
            if x[1].trim() == "*":
                me = True
            else:
                me = False

        if x[0] == "Disallow":
            if me and x[1] != "":
                disallowed.append(x[1])
    return disallowed

    

def crawl(root, maxPages):
    onlyTheseDomains = ["www.concordia.ca", "concordia.ca"]
    
    root=root
    rootParsed = urlparse(root)
    time_=0
    urlQueue = []
    urlQuantity = 0
    #interval between successive requests from the same domain
    politenessInterval = 20
    currentPage = None
    crawledTime = {}
    crawled = []
    exclusions = {}
    
    #method to scrape the page data
    def scrape(url):
        parsed = urlparse(url)
        allowed = True
        page = None
        nonlocal urlQuantity
        nonlocal crawledTime
        nonlocal crawled
        
        if fileChecker(url):
            if len(onlyTheseDomains) == 0 or parsed.netloc in onlyTheseDomains:      
                if parsed.netloc not in exclusions.keys():
                    exclusions[parsed.netloc] = checkPermissions(parsed.netloc)
                if "/" not in exclusions[parsed.netloc]:
                    for path in exclusions[parsed.netloc]:
                        if allowed and re.search(path, parsed.path):
                            allowed = False
                else:
                    allowed = False
                if allowed:
                    try:
                        print(time.localtime(time.time()).tm_sec,": ping!")
                        page = requests.get(url, timeout = 5)
                        crawledTime[parsed.netloc] = time.time()
                        crawled.append(url)
                    except Exception:
                        print(Exception, "\n", url)
                        page = None
                if page != None:
                    if page.status_code == 200:
                        urlQuantity += 1
                        page = p.page(urlQuantity,url,page.text)

        return page

    
    url  = check(root)
    currentPage = scrape(root)
    
    yield currentPage
    for url in currentPage.allLinks():
        urlQueue.insert(0, url)
    #while there are still urls to be parsed, it will go through the queue
    # if its a good url it will request from it and parse it, else it will
    #discard it
    while(maxPages != urlQuantity and len(urlQueue) != 0):
        n = urlQueue.pop()
        n = check(n)
        parsed = urlparse(n)
        domain = parsed.netloc

        badURL = False
        if n not in crawled:
            x = domain in crawledTime.keys()
            y = False
            if x:
                y = (time.time() - crawledTime[domain]) > politenessInterval
            else:
                y = True
            z = domain not in crawledTime.keys()
            if (x and y) or y:
                try:
                    
                    currentPage = scrape(n)
                    if currentPage != None:
                        for url in currentPage.allLinks():
                            urlQueue.insert(0,url)
                        yield currentPage
                except Exception as e:
                    print(e)
                    print(n)
                    badURL = True
            elif not badURL:
                urlQueue.insert(0,n)
    print("Crawled",len(crawled),"sites")


