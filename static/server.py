from flask import Flask, render_template, request, redirect
import queryProcessor  as q
import os, json, re
from nltk.corpus import stopwords
stop_words = stopwords.words('english')

app = Flask(__name__)


@app.route("/", methods=["POST","GET"])
def home():
    return render_template("base.html")

@app.route("/queryProcessing/<string:query>", methods=["GET","POST"])
def retrieve(query):
    print("Query:",query)
    query = re.sub(r'[^\w\s]','',query)
    query = re.sub('/[,/\!@#$%^&*()=-_+]+/g','',query)
    print("Starting processing")
    query = query.split()
    queryLst = []
    for q_ in range(len(query)):
        if query[q_].lower() not in stop_words:
            queryLst.append(query[q_].lower())
    results = q.queryProcessorRankedOR(queryLst,"Blocks/Index.txt")
    ret = {}
    print(type(results),len(results))
    print("brf")
    with open('urls.json','r') as urls:
        file = urls.read()
        cont = json.loads(file)
        j = 0
        for i in results:
            if j == 15:
                break
            ret[j]=cont[str(i)]
            j += 1
    
    return ret

if __name__=='__main__':
    app.run(debug=True)
