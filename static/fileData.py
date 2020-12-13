import extractor, re
from urllib.parse import urlparse
class page:
    def __init__(self, ID, url, raw):
        parsed = urlparse(url)
        self.ID = ID
        self.url = url
        self.raw = raw
        self.domain = parsed.netloc
        self.allTags = extractor.returnAllTags(raw)
        
        
        self.allSites = re.findall("https?://[www\.]?[a-zA-Z0-9]+(?:\.[a-zA-Z]+){1,61}[a-zA-Z0-9/\\\.?\:!@#$%^&*]+", raw)

    def getTags(self):
        return extractor.returnAllTags(self.raw)    

    def getID(self):
        return ID

    def getUrl():
        return url

    def getRaw():
        return raw

    def getTags(self):
        return allTags

    def allLinks(self):
        links = []
        for link in extractor.allIDExtractor("href",self.raw):
            if link not in self.allSites and link not in links:
                if link[0] == "/":
                    link = self.domain + link
                links.append(link)
        self.allSites = links
        return links
