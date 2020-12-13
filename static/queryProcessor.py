import json, math, blockMerge                                         
import nltk
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
#input of some query

#For a reasonable sized index that may fit in memory,
#This will load the entirity of it to memory to improve
#search times
def loadIndexToMemory(indexFile):
    dex = []
    returnDict = {}
    with open(indexFile,'r') as index:
        dex = index.readlines()
        for line in dex:
            temp = blockMerge.strIndexToDict(line)
            returnDict[temp[0]] = temp[1]
    return returnDict


#query input is a list of words, index is the path to the index file
def queryProcessorMem(query, index):
    #will then return the query that exists in the indicated index file
    memDex= loadIndexToMemory(index)
    postingsLists = []
    for term in query:
        if term in memDex.keys():
            postingsLists.append(memDex[term])
        
    return postingsLists

#sorts a set of lists by indicated idices in ascending order
def pairSortBubble(postings, indice):
    #willApply Bubble sort due to the posting lists are likely
    #to already be in order by docID and that is the primary indice
    #I currently need to sort it by, so it will likely have best
    #time of n instead of n^2
    newPost = postings
    for i in range(len(postings)):
        for k in range(0,len(postings)-i-1):
            if newPost[k][indice] < newPost[k+1][indice]:
                temp = newPost[k+1] 
                newPost[k+1] = newPost[k]
                newPost[k] = temp
    
    return newPost
               
    
#input queryTerms is a list of query terms, index ->indexFile
def queryProcessorAND(queryTerms, indexFile):
    postings = []
    finalOutput = []
    places = []
    addFlag = True
    
    #helper method, tells the while Loop when to stop
    def notAnyEmpty(x):
         for a in range(len(x)):
             if places[a] == len(x[a]):
                 return False
         return True
    
    #will initialize the posting lists of the query terms
    # to then find the intersection
    queryPostings = queryProcessorMem(queryTerms, indexFile)

    if len(queryPostings) != len(queryTerms):
        print(len(queryPostings),len(queryTerms))
        return []
    #will make sure lists are sorted
    for i in range(len(queryPostings)):
        postings.append(pairSortBubble(queryPostings[i],0))
        places.append(0)
    
    #starting point for comparison
    gcd = postings[0][places[0]][0]

    #while all the lists are not empty
    #if all the currently pointed to are the same
    #it will then add the term to the final list
    #and increment all pointers, else it will contantly try to
    #find the greatest common number, so it will increment
    #anything less than the gcd until they are equal
    while(notAnyEmpty(postings)):
        addFlag = True
        
        if addFlag:
            for i in range(len(postings)):
                if postings[i][places[i]][0] != gcd:
                    addFlag = False
                    break
                
            if addFlag:
                finalOutput.append(postings[0][places[0]][0])
                for i in range(len(places)):
                    places[i]+=1
            else:
                for i in range(len(postings)):
                    pst = postings[i][places[i]][0]
                    if pst > gcd:
                        gcd = pst
                for i in range(len(postings)):
                    pst = postings[i][places[i]][0]
                    if pst != gcd:
                        places[i]+=1    
                       
    return finalOutput

#input queryPostings ->[[(int,int),(int,int),..],[(int,int),(int,int),...]]
#input postinglist -> [int, int, int,...]
#will sort the postings list of an OR query based on how many 
def sortPostingsOR(queryPostings, postingList):
    finalPostings = []
    finalPostings2 = []
    queryPostings2 = []
    for i in range(len(queryPostings)):
        queryPostings2.append([])
        for k in range(len(queryPostings[i])):
            queryPostings2[i].append(queryPostings[i][k][0])
    #Will create pairs of postings and how many terms appear in the posting
    for i in postingList:
        count = 0
        for k in range(len(queryPostings2)):
            if i in queryPostings2[k]:
                count +=1
        finalPostings.append((i, count))

    #will sort the postings by the indice indicating how many search terms are
    #in it
    finalPostings = pairSortBubble(finalPostings,1)

    #since the search returns in ascending order, will put it in descending
    #order so that it is mostTermsPresent -> leastTermsPresent
    for i in range(len(finalPostings)):
        finalPostings2.insert(0,finalPostings[i][0])
    return finalPostings2
    
    
#Will take a list of query terms and indexFile path and return
#a sorted postings list by how many occurances of each word each file has
# for the union of all posting lists
def queryProcessorOR(queryTerms, indexFile):
    postings = []
    finalOutput = []
    places = []
    addFlag = True
    
    #condition for the while loop to stop
    def notAllEmpty(x):
         for a in range(len(x)):
             if places[a] < len(x[a]):
                 return True
         return False
    
    #will collect and initiallize the posting lists
    queryPostings = queryProcessorMem(queryTerms, indexFile)
    
    
    for i in range(len(queryPostings)):
        postings.append(pairSortBubble(queryPostings[i],0))
        places.append(0)
    
    #start value to compare
    min = postings[0][places[0]][0]
    
    
    #while not all postings are empty will add the min value among
    #them to the final list, then increment the added values until all
    #lists are empty
    while(notAllEmpty(postings)):
        ptr = 0
        while(places[ptr] == len(postings[ptr])):
            ptr += 1
        min = postings[ptr][places[ptr]][0]
        
        for i in range(len(postings)):
            if places[i] != len(postings[i]):
                pst = postings[i][places[i]][0]
                if pst < min:
                    min = pst
        finalOutput.append(min)
        for i in range(len(postings)):
            if places[i] != len(postings[i]):
                pst = postings[i][places[i]][0]
                if min == pst:
                    places[i]+=1
    #will sort the final list by how many terms are in it in
    #descending order
    finalOutput = sortPostingsOR(queryPostings,finalOutput)
                    
    return finalOutput


#will rank the Index at designated location and create a json file with
#the ranking of each document
def BM25RankPostings(query, postings,indexName):
    #sum for each term in the query of
    #log(N/df)*((k1+1)*tf)/(k1*((1-b)+b*Ld/Lave)+tf)
    #N = Number of docs
    #k1 is a positive scaling number for tf
    #b is a parameter 0<=b<=1
    terms = loadIndexToMemory(indexName)
    ranking = 0
    k1 = 1.6
    b = .75
    N = 0
    Lave = 0
    Ld = 0
    LdAll = 0
    rankedIndex = {}
    docIDs = []

    """
    for each posting:
        for each term in that postings
            give a score, then add it to a total score for that doc

    """
    with open("BM25Info.json",'r') as docInfo:
        allDocs = json.loads(docInfo.read())
        N = len(allDocs)
        for doc in allDocs:
            LdAll += allDocs[doc]
        for doc in postings:
            rankedIndex[doc]=0
        Lave = LdAll/N
        
        for doc in postings:
            for q in query:
                if q in terms.keys():
                    #Will not calculate for stopwords since they are likely in
                    #more than half the documents and will likely give negative
                    #values based on the BM25 formula used
                    tf = -1
                    for i in range(len(terms[q])):
                        if terms[q][i][0] == doc:
                            tf = terms[q][i][1]
                    if tf == -1:
                        continue
                    Ld = allDocs[str(doc)]
                    df = len(terms[q])
                    ranking = math.log(N/df)*(((k1+1)*tf)/(k1*((1-b)+b*Ld/Lave)+tf))
                    rankedIndex[doc] += ranking

        for key in rankedIndex:
            docIDs.append((int(key),rankedIndex[key]))
        x = pairSortBubble(docIDs,1)
        
        return x
        

#With the input of a postings list, will return sorted by document
#ranking the same postings list
def returnRankedOrderedPostings(postings):
    orderedRanked = []
    final = []
    with open("RankedIndex.json",'r') as index:
        ranks = json.loads(index.read())
        for post in postings:
            pair = (post,ranks[str(post)])
            orderedRanked.append(pair)
        orderedRanked = pairSortBubble(orderedRanked,1)
    for post in orderedRanked:
        final.append(post[0])
    return final

def queryProcessorRankedOR(queryTerms, IndexFile):

    
    postings = queryProcessorOR(queryTerms,IndexFile)

    
    ret1=BM25RankPostings(queryTerms, postings,IndexFile)
    ret2 = []
    for i in ret1:
        ret2.append(i[0])
    
    return ret2
