import re, os, nltk, json, time
from nltk import word_tokenize
import extractor, tokenizer, blockMerge, selfCrawler
start_time=time.time()

import argparse
def init_params():
    parser = argparse.ArgumentParser(description='Process input path parameter.')
    parser.add_argument('-M','--Max', default=50, help='Max pages to crawl.')
    parser.add_argument('-r','--root', default="https://concordia.ca", help='Starting root to crawl from.')
    parser.add_argument('-e','--exclude', default=[], help='Pages to not crawl to.')
    parser.add_argument('-o','--Only', default=[], help='Only pages to crawl on.')
    parser.add_argument('-b','--blockSize', default=500, help='What the block size in SPIMI will be')
    init_params.args = parser.parse_args()
    return init_params.args
    
args = init_params()

docLengths = {}
docTotal = 0


def tokenStream(root, maxPages):
    urlDex = {}
    docTotal = 0
    for page in selfCrawler.crawl(root,maxPages):
        docTotal += 1
        raw = page.raw
        ID = page.ID
        url = page.url
        urlDex[ID] = url
        txtIDPair = {}
        print(ID)
        if raw != None:
            try:
                txtIDPair["TEXT"] = extractor.ConcordiaPageExtract(raw)
            except Exception:
                print(Exception,len(raw))
                txtIDPair["TEXT"] = None
                print(ID," : ", url)
        else:
            txtIDPair["TEXT"] = None
        if txtIDPair["TEXT"] == None:
            docLengths[ID] = 0
        else:
            docLengths[ID] = len(txtIDPair['TEXT'])
        txtIDPair["ID"] = ID
        if txtIDPair["TEXT"] != None:
            docLengths[txtIDPair["ID"]] = len(txtIDPair["TEXT"])
        for token in tokenizer.tokenizer(txtIDPair):
            token = (token[0],token[1].lower())
            
            yield token
    with open("urls.json",'w') as map:
        x = json.dumps(urlDex,sort_keys = True, indent = 2)
        map.write(x)


#takes list of tuples (ID,Token)
#ID -> (ID,tf)
#takes string object of "term":[(ID,tf),(ID,tf)...] and converts to dict item
def SPIMI(tokenStream, blockSize):

    emptyCount = 0
    block = {}
    blockCounter = 0
    tokenCounter = 0
    fileOpenLimit = 1000

    #Creates or cleans the files or paths before starting the process
    if not os.path.exists("Blocks") or not os.path.isdir("Blocks"):
        os.mkdir("Blocks")
    if os.path.exists('Blocks/*'):
        os.remove('Blocks/*')
    #will take in a tokenStream and record in a block until the block is full
    #for each token in string format so that they may be more easily streamed
    #line by line in the next step
    for token in tokenStream:
        if token[1] == None or token[1] == []:
            print(token)
        tokenCounter += 1
        if token[1] != None:
            #Appends the posting lists of two terms in a block if they share
            # a term
            if token[1] in block.keys():
                for i in range(len(block[token[1]])):
                    if block[token[1]][i][0] == token[0]:
                        block[token[1]][i] = (block[token[1]][i][0],block[token[1]][i][1]+1)
                        break
                    elif i == len(block[token[1]])-1:
                        block[token[1]].append((token[0],1))
            else:
                block[token[1]] = [(token[0],1)]
        #Dumps the block into a file then restarts when the block becomes full
        if tokenCounter == blockSize:
            with open('Blocks/Block-'+str(blockCounter)+'.txt','w') as out:
                for key in sorted (block.keys()):
                    out.write('\"'+key+'\"'+":"+str(block[key])+"\n")
                blockCounter += 1
                block = {}
                tokenCounter = 0

    #Do this if there are too many blocks that will crash if opened in memory,
    #aka the 1024 file limit in linux
    if blockCounter > fileOpenLimit:
        for x in range(round(blockCounter/fileOpenLimit)+1):
            ub = x*fileOpenLimit#upper bound of open files
            blockMerge.blockFileMerge(ub,fileOpenLimit+ub,"Block","Index-"+str(x),False)
    
        blockMerge.blockFileMerge(0,round(blockCounter/fileOpenLimit),"Index","Index",False)    
    #Does this if there are few enough blocks that opening all of them in memory won't cause a too many files open error
    else:
        blockMerge.blockFileMerge(0,blockCounter,"Block","Index",False)
        




#SPIMI(tokenStream(path),10000)

SPIMI(tokenStream("https://www.concordia.ca",10000),args.blockSize)


print("Seconds: ",time.time()-start_time)
print("Minutes: ",(time.time()-start_time)/60)

with open("BM25Info.json", "w") as BM25:
    BM = json.dumps(docLengths,sort_keys=True)
    BM25.write(BM)
