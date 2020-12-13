import re, json
#Method will return the contents within a desired tag name as a string excluding the tag
def tagExtractor(tagName, txt):
    #flag will indicate when to record characters between the tags
    doc_flag = False
    doc = ""
    #will for the length of the inputted text run a character at a time,
    #if it matches a '>' character and is preceeded by the tag will turn on
    #the flag, if comes across a '<' and is followed by '/'+the tag name will
    #return the recorded string.
    for char in range(len(txt)):
        if txt[char] == '<' and txt[char+1:char+1+len(tagName)]==tagName:
            doc_flag = True
        if doc_flag and txt[char] == '>' and txt[char-len(tagName)-1:char]=='/'+tagName:
            doc+=txt[char]
            doc_flag = False
            return doc
        if doc_flag:
            doc+=txt[char]

            
def allTagExtractor(tagName, txt):
    #flag will indicate when to record characters between the tags
    doc_flag = False
    doc = ""
    #will for the length of the inputted text run a character at a time,
    #if it matches a '>' character and is preceeded by the tag will turn on
    #the flag, if comes across a '<' and is followed by '/'+the tag name will
    #return the recorded string.
    for char in range(len(txt)):
        if txt[char] == '<' and txt[char+1:char+1+len(tagName)]==tagName:
            doc_flag = True
        if doc_flag:
            doc+=txt[char]
        if doc_flag and txt[char] == '>' and txt[char-len(tagName)-1:char]=='/'+tagName:
            doc+=txt[char]
            doc_flag = False
            start_flag = False
            yield doc[1:len(doc)-len(tagName)-1]
            doc = ""
            

#Will search a text for an ID name, then return the value recorded in its
#quotations assigned to it
def IDExtractor(IDName, txt):
    doc_flag = False
    doc = ""
    pair = 0
    for char in range(len(txt)):
        if doc_flag and txt[char] == '\"':
            pair +=1
        if txt[char] == IDName[0] and txt[char:char+len(IDName)] == IDName:
            doc_flag = True
        if doc_flag and txt[char]== '\"' and pair == 2:
            doc_flag = False
            return doc
            doc = ""
            pair = 0
        if doc_flag and re.search('[0-9]',txt[char]):
            doc+=txt[char]

            
#Will Yield the ID rather than just return the first instance
def allIDExtractorNum(IDName, txt):
    doc_flag = False
    doc = ""
    pair = 0
    for char in range(len(txt)):
        if doc_flag and txt[char] == '\"':
            pair +=1
        if txt[char] == IDName[0] and txt[char:char+len(IDName)] == IDName:
            doc_flag = True
        if doc_flag and txt[char]== '\"' and pair == 2:
            doc_flag = False
            yield doc
            doc = ""
            pair = 0
        if doc_flag and re.search('[0-9]',txt[char]):
            doc+=txt[char]


def allIDExtractor(IDName, txt):
    tag_found = False
    recording = False
    doc = ""
    allDoc = []
    pair = 0
    for char in range(len(txt)):
        if tag_found and txt[char-1] == '\"' and txt[char-2] == "=":
            recording = True
        if txt[char] == IDName[0] and txt[char:char+len(IDName)+1] == IDName+"=":
            tag_found = True
        if recording  and txt[char]== '\"' and txt[char-1] != "=":
            recording = False
            tag_found = False
            yield doc
            doc = ""
        if recording:
            doc+=txt[char]

            

#Will clean up an extracted block by removing the outermost html tags            
def removeEndTags(txt):
    start_pos = 0
    end_pos = 0
    for char in range(len(txt)):
        if txt[char] == '>':
            start_pos = char+1
            break
    for char in range(len(txt)):
        if txt[len(txt)-char-1] == '<':
            end_pos = len(txt)-char
            break
    if end_pos != 0:
        return txt[start_pos:end_pos]
    else:
        return txt[start_pos:]

def returnAllTags(txt):
    tags = []
    currentTag = ""
    recordFlag = False
    for char in range(len(txt)):
        if txt[char-1] == '<' and txt[char] != '/':
            recordFlag = True

        elif txt[char] == '>' or txt[char] == " ":
            recordFlag = False
            if currentTag not in tags:
                tags.append(currentTag)
            currentTag = ""
        
        if recordFlag:
            currentTag += txt[char]

    return tags


#returns tags with ID value for the designated ID name

#step one, record the tag name only if it is not recording the text body

#step two, see if it has the desired ID

#if it does it will need to check the value of the ID
#otherwise it will just continue on with life

#if the value matches, once it reaches the end bracer start recording

#if it encounters a tagname that is the same as original's, add to stack
#then pop if it encounters the matching closing bracket

#if it reaches a matching end tag and the stack is empty stop recording
#and start over with recording tag
def returnTWIV(txt, ID, val):
    recordTag = False
    checkVal = False
    correctVal = False
    recordVal = False
    recording = False
    tagName = ""
    IDval = ""
    returnText = ""
    dups = 0
    for char in range(len(txt)):
        

        #step one, record the tag name only if it is not recording the text body
        if not correctVal and txt[char-1] == "<" and txt[char] != "/":
            recordTag = True
        elif not correctVal and (txt[char] == " " or txt[char] == ">"):
            recordTag = False
        if recordTag:
            tagName += txt[char]
        #step two, see if it has the desired ID
        
        if not correctVal and txt[char] == ID[0] and txt[char:char+len(ID)+1] == ID+"=":
            checkVal = True
        #if it does it will need to check the value of the ID
        #otherwise it will just continue on with life

        if checkVal and txt[char-1] == "\"" and txt[char-2] == "=":
            recordVal = True
        elif checkVal and txt[char] == "\"" and txt[char-2] !="=":
            recordVal = False
            #checks the value
   
            if val in IDval.split():
                correctVal = True
            IDval = ""

        if recordVal:
            IDval += txt[char]

        #if the value matches, once it reaches the end bracer start recording
        if correctVal and txt[char-1] == ">" and not recording:
           recording = True
        #if it encounters a tagname that is the same as original's, add to stack
        #then pop if it encounters the matching closing bracket
        if len(txt)-char > len(tagName) and tagName != "":
        
            if recording and txt[char] == tagName[0] and txt[char:char+len(tagName)] == tagName and txt[char-1] == "<":
                dups += 1
            elif recording and txt[char] == tagName[0] and txt[char:char+len(tagName)] == tagName and txt[char-2:char] == "</" and dups > 0:
                dups -= 1

        #if it reaches a matching end tag and the stack is empty stop recording
        #and start over with recording tag
            
        if recording and dups == 0 and tagName != "" and txt[char] == tagName[0] and txt[char-2:char+len(tagName)] == "</"+tagName:
            recording = False
            correctVal = False
            tagName = ""
            returnText += " "


        if recording:
            returnText += txt[char]
        elif txt[char-1] == ">" and not recordTag:
            tagName = ""
            
        
    return returnText[:len(returnText)-2]

    

def removeAllTags(txt):
    rem = False
    ret = ""
    for char in range(len(txt)):
        if not rem and txt[char] == "<":
            rem = True
        elif txt[char] == ">":
            rem = False
            ret += " "
        if not rem:
            ret += txt[char]
    return ret

def getKeywords(txt):
    recording = False
    goodToGo = False
    recordKeyWords = False
    start = False
    toMatch = "http-equiv=\"keywords\""
    ret = ""
    for char in range(len(txt)):
        if not recording and txt[char] == "<":
            recording = True

        if recording:
            if txt[char] == toMatch[0] and txt[char:char+len(toMatch)] == toMatch:
                goodToGo = True
            
        if not goodToGo and recording and txt[char] == ">":
            recording = False
            ret = ""

        if goodToGo and txt[char] == "c" and txt[char:char+7] == "content":
            recordKeyWords = True
            ret = ""

        if recordKeyWords and txt[char-1]=="\"" and txt[char-2] == "=": 
            start = True
        if start and txt[char] != "\"":
            ret += txt[char]
        elif start and txt[char] == "\"":
            return ret.replace(",","")

    
 
def ConcordiaPageExtract(raw):
    impTags = ["table"]
    impClasses = ["event-title","subtitle","text","large-text","news-title"]
    impIDs = ["content-main"]
    #impContent = ["http-equiv=\"keywords\""]
    final = ""
    
    final += getKeywords(raw)+" "
    """
    for value in impClasses:
        final += returnTWIV(raw, "class", value)+" "
    print(len(final))
    """
    for value in impIDs:
        final += returnTWIV(raw, "id", value)+" "
    """  
    for tag in impTags:
        x = tagExtractor(tag,raw)
        if x != None:
            final += x+" "
    """
    final =  removeAllTags(final)
    final = final.replace("\n"," ")
    final = final.replace("\r"," ")
    final = final.replace("\t"," ")
    final = final.replace(">"," ")
    final = final.replace("â"," ")
    return final
    
