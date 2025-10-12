from flask import Flask, render_template, request, redirect
import queryProcessor  as q
import os, json, re
from nltk.corpus import stopwords
from werkzeug.middleware.proxy_fix import ProxyFix
stop_words = stopwords.words('english')

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
@app.route("/", methods=["POST","GET"])
def home():
    return render_template("base.html")

@app.route("/queryProcessing/<string:query>", methods=["GET","POST"])
def retrieve(query):
    print("Query:",query)
    query = re.sub(r'[^\w\s]','',query)
    query = re.sub('/[,/@#$%^&*()=-_+]+/g','',query)
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

@app.route("/status", methods=["GET"])
def status():
    return {'message': 'OK', 'code': 200}, 200

@app.route("/query/<string:query>", methods=["GET"])
def query(query):
    print("Query:",query)
    query = re.sub(r'[^\w\s]','',query)
    query = re.sub('/[,/@#$%^&*()=-_+]+/g','',query)
    print("Starting processing")
    query = query.split()
    queryLst = []
    for q_ in range(len(query)):
        if query[q_].lower() not in stop_words:
            queryLst.append(query[q_].lower())
    results = q.queryProcessorRankedOR(queryLst,"Blocks/Index.txt")
    ret = {'code': 200, 'message': []}
    with open('urls.json','r') as urls:
        file = urls.read()
        cont = json.loads(file)
        j = 0
        for i in results:
            ret['message'].append(cont[str(i)])
            j += 1    
    return ret, 200

if __name__=='__main__':
    app.run(debug=False)
