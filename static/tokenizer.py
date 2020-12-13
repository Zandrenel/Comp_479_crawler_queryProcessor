import nltk, re
from nltk.corpus import stopwords
from nltk import word_tokenize
stop_words = set(stopwords.words('english'))


def tokenizer(dict_):
    if dict_ != None:
        docTxt = dict_['TEXT']
        """If the text is not empty, it will separate anything dividedby a '/',
      then remove puctuation and numbers before finally Tokenizing the string. Then
      for each token it will be returned in a tuple with the ID of the document it was
      from """
        if docTxt == None:
            docTxt = ""
        for char in range(len(docTxt)):
            if docTxt[char] == '/' and re.search("[a-zA-Z]/[a-zA-Z]",docTxt[char-1:char+2]):
                docTxt = docTxt.replace("/", " ")
        docTxt = re.sub(r'[^\w\s]','',docTxt)
        docTxt = re.sub('/[,/\!@#$%^&*()=-_+]+/g',' ',docTxt)
        docTokens = word_tokenize(docTxt)
        for token in docTokens:
            token = token.lower()
            temp = token.replace("-","")
            temp = temp.replace(".","")
            if token not in stop_words and not temp.isnumeric() and len(token)<50:
                yield (dict_["ID"],token)


