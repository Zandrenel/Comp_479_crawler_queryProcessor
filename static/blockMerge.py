import os

#helper method for SPIMI, determines if the blocks are all empty
def blockNotEmpty(lst):
    for i in lst:
        if i != None and i != "":
            return True
    return False

#helper method for SPIMI, extracts STR:[(int,int),(int,int)...] from Str
def strIndexToDict(Str):
    if Str.strip() != "" and Str != None and Str.strip() != None :
        parts = Str.split(":")
        parts[0] = parts[0].strip("\"")
        parts[1] = parts[1].replace("),","|")
        parts[1] = parts[1].replace("("," ")
        parts[1] = parts[1].replace("["," ")
        parts[1] = parts[1].replace("]"," ")
        parts[1] = parts[1].replace(")"," ")
        tuples = parts[1].split("|")
        newList = []
        for tup in tuples:
            t = tup.split(",")
            newList.append((int(t[0].strip()),int(t[1].strip())))
        return (parts[0],newList)



def blockFileMerge(startBlock, endBlock, blockPrefix, output, jsonify):
    start = startBlock
    end = endBlock
    allBlocks = []
    topLayer = []
    minVal = None
    fromBlocks = []
    with open('Blocks/'+output+'.txt','w') as index:
        #will write in a json looking format if true
        if jsonify:
            index.write("{")
        #Open all Blocks
        for i in range(start,end):
            blockName = 'Blocks/'+blockPrefix+'-'+str(i)+'.txt'
            if os.path.exists(blockName):
                allBlocks.append(open(blockName))
                topLayer.append(allBlocks[i-start].readline())
        while(blockNotEmpty(topLayer)):
            #find the min value in top layer of the block
            #first sets a base value to compare the others
            #with as the first non empty block
            pointer = 0
            while(topLayer[pointer]==None or topLayer[pointer].strip()==""):
                  pointer += 1
            minVal = strIndexToDict(topLayer[pointer])
            minVal = minVal[0]

            
            for i in range(len(allBlocks)):
                term = strIndexToDict(topLayer[i])
                if term != None and term != "" and term[0] != None:
                    term = term[0]
                    if term == minVal:
                        fromBlocks.append(i)
                    elif term < minVal:
                        minVal = term
                        fromBlocks = [i]
                        
            #merge all occurances of the term's posting list if multiple
            if len(fromBlocks) > 1:
                finalPostings = []
                for j in fromBlocks:
                    if topLayer[j]!=None and topLayer[j].strip() != "":

                        postings = strIndexToDict(topLayer[j])
                        if postings != None:
                            postings = postings[1]

                        #It will merge the posting lists of all the lists
                        #from all blocks that contained the term, also
                        #incrementing the recorded term frequency if needed
                        if len(postings) > 0:
                            for i in range(len(postings)):
                                for k in range(len(finalPostings)):
                                    if postings[i][0] == finalPostings[k][0]:
                                        x = postings[i][1] + finalPostings[k][1]
                                        finalPostings[k] = (finalPostings[k][0],x)
                                    elif k == (len(finalPostings)-1):
                                        finalPostings.append(postings[i])
                                if len(finalPostings)==0:
                                   finalPostings.append(postings[i])
                    #increment added values

                        topLayer[j] = allBlocks[j].readline()

                #Where the lease term is written to the index
                termPost = "\""+str(minVal)+"\":"+str(finalPostings)

                if blockNotEmpty(topLayer):
                    if jsonify:
                        index.write(termPost+",\n")
                    else:
                        index.write(termPost+"\n")
                else:
                    if jsonify:
                        index.write(termPost+"\n}")
                    else:
                        index.write(termPost+"\n")
            else:
                #Where the least term is written to the index if it
                # was in only 1 doc
                termPost = "\""+str(minVal)+"\":"+str(strIndexToDict(topLayer[fromBlocks[0]])[1])
                if blockNotEmpty(topLayer):
                    if jsonify:
                        index.write(termPost+",\n")
                    else:
                        index.write(termPost+"\n")
                else:
                    if jsonify:
                        index.write(termPost+"\n}")
                    else:
                        index.write(termPost+"\n")
                topLayer[fromBlocks[0]] = allBlocks[fromBlocks[0]].readline()

    #Delete the blocks to be polite
    for i in range(start,end):
        blockName = 'Blocks/'+blockPrefix+'-'+str(i)+'.txt'
        if os.path.exists(blockName):
            os.remove(blockName)
