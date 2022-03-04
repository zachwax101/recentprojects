import string

from decimal import *
getcontext().prec = 1000


def compareSpaceLess(s1, s2):
    return s1.strip() == s2.strip()

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

outputFile = open("submission.pos", "w")

transitions = {}
trigram = {}
likelihood = {}
vocab = []
firstTri = ""
sndTri = ""





i = 0

###first training file
with open('WSJ_02-21.pos') as file:
    #deal with first line
    firstLine = file.readline()
    splited = firstLine.split()
    prevPos = splited[1]

    for line in file:
        if line.isspace(): #dealing with EOS = end of sentence
            
            if "EOS" in transitions:
                if prevPos in transitions["EOS"]:
                    transitions["EOS"][prevPos] = transitions["EOS"][prevPos] + 1
                else:
                    transitions["EOS"][prevPos] = 1
            else: #first time
                transitions["EOS"] = {prevPos : 1}
            prevPos = "EOS"
        else:
            splited = line.split()
            curPos = splited[1]
            curWord = splited[0].strip().lower()
            if curPos in transitions:
                if prevPos in transitions[curPos]:
                    transitions[curPos][prevPos] = transitions[curPos][prevPos] + 1
                else:
                    transitions[curPos][prevPos] = 1
            else: #first time
                transitions[curPos] = {prevPos : 1}
            ####trigram####
            if curPos in trigram:
                if firstTri in trigram[curPos]:
                    if sndTri in trigram[curPos][firstTri]:
                        trigram[curPos][firstTri][sndTri] = trigram[curPos][firstTri][sndTri] + 1
                    else:
                         trigram[curPos][firstTri][sndTri] = 1
                else:
                    trigram[curPos][firstTri] = {sndTri : 1}
            else:
                #trigram[curPos][firstTri][sndTri] = {curPos: {firstTri: {sndTri : 1}}}
                dict_a = {}
                dict_b = {}
                dict_a[firstTri] = dict_b
                dict_b[sndTri] = 1
                trigram[curPos] = dict_a

            ########
            #deal with liklihood
            if curPos in likelihood:
                if curWord in likelihood[curPos]:
                    likelihood[curPos][curWord] = likelihood[curPos][curWord] + 1
                else:
                    likelihood[curPos][curWord] = 1
            else:
                likelihood[curPos] = {curWord : 1}
            #fill list 
            if curWord not in vocab:
                vocab.append(curWord)  

            if i > 2:
                firstTri = curPos
                sndTri = prevPos

            prevPos = curPos 

            i = i +1

file.close()

###second training file
with open('WSJ_24.pos') as file:
    #deal with first line
    firstLine = file.readline()
    splited = firstLine.split()
    prevPos = splited[1]

    for line in file:
        if line.isspace(): #dealing with EOS = end of sentence
            if "EOS" in transitions:
                if prevPos in transitions["EOS"]:
                    transitions["EOS"][prevPos] = transitions["EOS"][prevPos] + 1
                else:
                    transitions["EOS"][prevPos] = 1
            else: #first time
                transitions["EOS"] = {prevPos : 1}
            prevPos = "EOS"
        else:
            splited = line.split()
            curPos = splited[1]
            curWord = splited[0].strip().lower()
            if curPos in transitions:
                if prevPos in transitions[curPos]:
                    transitions[curPos][prevPos] = transitions[curPos][prevPos] + 1
                else:
                    transitions[curPos][prevPos] = 1
            else: #first time
                transitions[curPos] = {prevPos : 1}

            #deal with liklihood
            if curPos in likelihood:
                if curWord in likelihood[curPos]:
                    likelihood[curPos][curWord] = likelihood[curPos][curWord] + 1
                else:
                    likelihood[curPos][curWord] = 1
            else:
                likelihood[curPos] = {curWord : 1}

            #fill list 
            if curWord not in vocab:
                vocab.append(curWord)           
            prevPos = curPos 

file.close()

totals = {}
for key in transitions:
    total = 0
    for nestedKey in transitions[key]:
        total = total + transitions[key][nestedKey]
    totals[key] = total

transLike = {}

for key in transitions:
    transLike[key] = {}
    for nestedKey in transitions[key]:
        transLike[key][nestedKey] = Decimal((transitions[key][nestedKey]))/Decimal(totals[key])

likeTotals = {}


rareWords = []

for key in likelihood:
    total = 0
    for nestedKey in likelihood[key]:
        total = total + likelihood[key][nestedKey]
        if(likelihood[key][nestedKey] < 5):
            rareWords.append(nestedKey)
    likeTotals[key] = total

likePropor = {}

grandTotal = 0

for key in totals:
    grandTotal += totals[key]

unigramDict = {}

for key in totals:
    unigramDict[key] = totals[key]/grandTotal

for key in likelihood:
    likePropor[key] = {}
    for nestedKey in likelihood[key]:
        likePropor[key][nestedKey] = Decimal(likelihood[key][nestedKey])/Decimal(likeTotals[key])



likePropor.pop("", None)
transLike.pop("", None)

for key in likePropor:
    likePropor[key].pop("", None)

for key in transLike:
    transLike[key].pop("", None)


###rarewords
rare_dict = {}
for key in likePropor:
    rareKeyScore = 0
    for nestedKey in likePropor[key]:
        if nestedKey in rareWords:
            rareKeyScore = rareKeyScore + likePropor[key][nestedKey]
    rare_dict[key] = rareKeyScore


######## open testing file
with open('WSJ_23.words') as file:
    #for first: get first prevPos, just a score 2
    firstWord = file.readline().strip(" ").strip("\n")
    firsLine = firstWord.lower()
    firstMaxScoreWord = 0
    curMaxPOSWO = 'bloop'

    for key in likePropor:
        for nestedKey in likePropor[key]:
            if compareSpaceLess(nestedKey, firsLine) and likePropor[key][nestedKey] > firstMaxScoreWord:
                curMaxPOSWO = key
                firstMaxScoreWord = likePropor[key][nestedKey]
                
    outputFile.write(firstWord + "\t" + curMaxPOSWO + "\n")

    prevPos = curMaxPOSWO
   

    for line in file:
        



        upperFlag = line[0].isupper()

        word = line.strip("\n").strip(' ').lower()
        

        if line.isspace():
            prevPos = "EOS"
            outputFile.write("\n")
            print("      :        EOS\n")
            continue
        elif has_numbers(word):
            outputFile.write(line.strip("\n").strip(' ') + "\t" + "CD" + "\n")
            prevPos = "CD"
        elif word == '"' or word == "%" or word == "&" or word == '$' or word == '``' or word == '(' or word == ")" or word == ',' or word == ':':
            outputFile.write(line.strip("\n").strip(' ') + "\t" + word + "\n")
            prevPos = word
        elif word == "-" or word == "--" or word == "---" or word == ";" or word  == '...' or word == '..':
            outputFile.write(line.strip("\n").strip(' ') + "\t" + ":" + "\n")
            prevPos = ":"
        elif word in vocab:
            curMaxCombo = 0
            curWinner = "bloop"
            curRunnerUp = "runnerUp"
            curRunnerUpScore = 0 
            curLikeScore = 0
            curTransScore = 0 
            for key in likePropor:
                for nestedKey in likePropor[key]:
                    if compareSpaceLess(nestedKey, word):
                        curLikeScore = likePropor[key][nestedKey]
                        if key in transLike:
                            if prevPos in transLike[key]:
                                curTransScore = transLike[key][prevPos]
                curScore = Decimal(curTransScore)*Decimal(curLikeScore)
                if curScore == 0:
                    curScore = curLikeScore
                if curScore > curMaxCombo:
                    curMaxCombo = curScore
                    curWinner = key
                elif curScore > curRunnerUpScore:
                    curRunnerUpScore = curScore
                    curRunnerUp = key
            if (curWinner == 'NN' or curWinner == 'JJ') and upperFlag == 1:
                curWinner = 'NNP'
            if(curWinner == 'LS' and curRunnerUp == 'JJ'):
                curWinner = ukRunner
            if(curWinner == 'VBG' and curRunnerUp == 'NN'):
                curWinner = curRunnerUp 
            if(curWinner == 'NNPS' and upperFlag != 1):
                curWinner = 'NNS'                
            if(word == 'a'):
                curWinner = 'DT'  

            prevPos = curWinner
            outputFile.write(line.strip("\n").strip(' ') + "\t" + curWinner + "\n")
            #print(word + " : " + curWinner + "\n")

        else: #unknown words
            maxScoreUnkWo = 0
            rareWordLikeCuScore = 0 
            winner = "shmoop"
            ukRunner = "blah"
            ukRuScore = 0
            for key in transLike:
                unknownWoCuScore = 0
                for nestedKey in transLike[key]:
                    if compareSpaceLess(nestedKey, prevPos):
                        if key in rareWords:
                            unknownWoCuScore = Decimal(transLike[key][nestedKey]) * Decimal(rare_dict[key])
                if unknownWoCuScore == 0:
                    unknownWoCuScore = transLike[key][nestedKey]
                if unknownWoCuScore > maxScoreUnkWo:
                    winner = key 
                    maxScoreUnkWo = unknownWoCuScore
                elif unknownWoCuScore > ukRuScore:
                    ukRuScore = unknownWoCuScore
                    ukRunner = key
            if (winner == 'NN' or winner == 'JJ') and upperFlag == 1:
                winner = 'NNP'
            if(winner == 'LS' and ukRunner == 'JJ'):
                winner = ukRunner
            if(winner == 'VBG' and ukRunner == 'NN'):
                winner = ukRunner
            if(winner == 'NNPS' and upperFlag != 1):
                winner = 'NNS'
            if(word == 'a'):
                winner = 'DT'  



            prevPos = winner
            outputFile.write(line.strip("\n").strip(' ') + "\t" + winner + "\n")
            #print(word + " : " + winner + "\n")



file.close()

