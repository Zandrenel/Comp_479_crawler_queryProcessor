import queryProcessor  as q
import os, json, re, sys
from nltk.corpus import stopwords
stop_words = stopwords.words('english')

query = sys.argv[1]

print("Query:",query)
query = re.sub(r'[^\w\s]','',query)
query = re.sub('/[,/\!@#$%^&*()=-_+]+/g','',query)

query = query.split()
queryLst = []
for q_ in range(len(query)):
    if query[q_].lower() not in stop_words:
        queryLst.append(query[q_].lower())
        results = q.queryProcessorRankedOR(queryLst,"Blocks/Index.txt")
        ret = {}
        print(type(results),len(results))
        
with open('urls.json','r') as urls:
    file = urls.read()
    cont = json.loads(file)
    j = 0
    for i in results:
        if j == 15:
            break
        print(cont[str(i)])

