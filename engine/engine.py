import math
import re
from stop_list import *

outputFile = open("output.txt", "w")
absFile = open("cran.all.1400")
queryFile = open("cran.qry")


def sortDictByValues(d):
    sorted_dict = sorted(d.items(), key=lambda x: x[1])    
    return sorted_dict

def trimAbVectorForQry(qryVector, abVector):
    newDict = {}
    for key in qryVector.keys():
        if key in abVector:
            newDict[key] = abVector[key]
        else:
            newDict[key] = 0
    return newDict

def cosSim(vec1, vec2):
    if len(vec1.keys()) != len(vec2.keys()):
        raise ValueError('cos Sim diff lengths')
    sumAB = 0
    sumAsq = 0
    sumBsq = 0
    for key in vec1:
        sumAB += vec1[key]*vec2[key]
        sumAsq += vec1[key]**2
        sumBsq += vec2[key]**2
    if math.sqrt(sumAsq*sumBsq) == 0:
        return 0
    return sumAB/(math.sqrt(sumAsq*sumBsq))

def rawTxtToListWords(rawTxt):
    rawTxtList = rawTxt.split(".I")
    rawTxtList.pop(0)
    for i in range(len(rawTxtList)):
        rawTxtList[i] = re.sub("s", "", re.sub(' +', " ", re.sub(r'[0-9]|/|\(|\)|\+|.W|.A|.B|.T|,', " ", rawTxtList[i].replace("\r", " ").replace("\n", " ").replace(".", " ")))).strip(" ")
    
    return rawTxtList

def vectorsMaker(listOfWordsOnlyTxt):  
    listOfAllWords = []
    for doc in listOfWordsOnlyTxt:
        for word in doc.split(" "):
            if word not in listOfAllWords and word not in closed_class_stop_words:
                listOfAllWords.append(word)
    #list of all words works, gives list of all words thourhgout all docs minus stop words

    TFvectors = []
    for doc in listOfWordsOnlyTxt:
        thisDocsTFVector = {}
        wordsInThisDoc = doc.split(" ")
        for word in wordsInThisDoc:
            if word in listOfAllWords:
                thisDocsTFVector[word] = float(wordsInThisDoc.count(word))
        TFvectors.append(thisDocsTFVector)
    ##for each doc, make a dict vector of non stop words, value = 0

    bigIDFDICT = {}
    for word in listOfAllWords:
        counter = 0
        for vec in TFvectors:
            if word in vec.keys():
                counter += 1
        IDF = math.log(len(TFvectors)/counter)
        bigIDFDICT[word] = IDF
    #bigIDF looks to work

    TFIDFVECTORS = []
    for i in range(len(TFvectors)):
        curTFIDF = {}
        for word in TFvectors[i].keys():
            curIDF = bigIDFDICT[word]
            curTFIDF[word] = TFvectors[i][word] * curIDF
        TFIDFVECTORS.append(curTFIDF)
    #adjust TFvectors to be TFIDF vectors, seems to work

    return TFIDFVECTORS


absRawTxt = absFile.read()
queryRawTxt = queryFile.read()
absTFIDFVECTS = vectorsMaker(rawTxtToListWords(absRawTxt))
qrsTFIDFVECTS = vectorsMaker(rawTxtToListWords(queryRawTxt))

resultsDict = {}
for i in range(len(qrsTFIDFVECTS)):
    resultsQry = {}
    for j in range(len(absTFIDFVECTS)):
        trimmedAbVect = trimAbVectorForQry(qrsTFIDFVECTS[i],absTFIDFVECTS[j])
        sim = cosSim(qrsTFIDFVECTS[i], trimmedAbVect)
        resultsQry[j] = sim
    resultsDict[i] = sortDictByValues(resultsQry)

for i in range(len(qrsTFIDFVECTS)):
    k = 0
    for j in reversed(range(len(absTFIDFVECTS))):
        outputFile.write(str(i+1) + " " + str(resultsDict[i][j][0]) + " " + str(resultsDict[i][j][1]) + "\n")
        k += 1
        if k >99:
            break
