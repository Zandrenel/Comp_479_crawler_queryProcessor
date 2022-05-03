import queryProcessor  as q
import os, json, re, sys
from nltk.corpus import stopwords
stop_words = stopwords.words('english')


path = sys.argv[1]

query = sys.argv[2]

query = re.sub(r'[^\w\s]','',query)
query = re.sub('/[,/\!@#$%^&*()=-_+]+/g','',query)

query = query.split()
queryLst = []

blocks = "{}/Blocks/Index.txt".format(path)
for q_ in range(len(query)):
    if query[q_].lower() not in stop_words:
        
        queryLst.append(query[q_].lower())

        
        results = q.queryProcessorRankedOR(queryLst,blocks,path)
        ret = {}
        
        
with open('{}/urls.json'.format(path),'r') as urls:
    file = urls.read()
    cont = json.loads(file)
    j = 0
    print(len(results))
    
    for i in results:
        #if j == 15:
        #    break
        
        print(cont[str(i)])
        j += 1
