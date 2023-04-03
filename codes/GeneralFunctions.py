"""
Created in 2016

@author: Xingpeng Li (xplipower@gmail.com)
"""


# //---  Read me  ---//
# Skip num lines when read a file;
# input variable f should be of file type.
def skipNLines(f, num):
    for i in range(0, num):
        f.readline()
    #return 

# //---  Read me  ---//
# Split a string based on delimiter (the input variable token), however, 
# any delimiter inside a pair of single quotes or double quotes
# will not be considered as a delimiter
def split(origStr, token, priorityToken):
    origStr = removeDoubleSlash(origStr)
    origStr = removeSpecialComments(origStr, "/*")
    origStr = origStr.replace("\"",priorityToken) # change double quotes to single quotes
    multiElem = []
    numPriorityToken = origStr.count(priorityToken)  # priorityToken is a single quote; it will be a problem if it can also be a double quote
    #numPriorityToken = origStr.count('\'')
    if numPriorityToken == 0:
        # there might be a problem if the first character is a comma, 
        # however, this kind of case does not seem to exist.
        multiElem = origStr.split(token)  # token should be a comma in this program
        return multiElem
    if numPriorityToken%2 == 1:
        print "Something is wrong in line: \n    " + origStr + \
                "\n  the number of " + priorityToken + " should be even (paired)."
        raise SystemExit
    idxPriorityToken = []
    copyStr = origStr
    idx = copyStr.find(priorityToken)
    idxOrig = idx
    while idx != -1:
        idxPriorityToken.append(idxOrig)
        copyStr = copyStr[(idx+1):]
        if not copyStr:
            break
        idx = copyStr.find(priorityToken)
        idxOrig += (idx+1)
    
    copyStr = origStr
    idxToken = copyStr.find(token)
    idxPreviousToken = -1
    idx = 0
    markLastIterPriorityToken = 0
    while idxToken != -1:
        if (idxToken < idxPriorityToken[idx]) or (idxToken > idxPriorityToken[idx+1]):
            if markLastIterPriorityToken == 0:
                multiElem.append(origStr[(idxPreviousToken+1):idxToken])
            else:
                markLastIterPriorityToken = 0
            copyStr = copyStr[:idxToken] + 'A' + copyStr[(idxToken+1):]
            idxPreviousToken = idxToken
            idxToken = copyStr.find(token)
            if (idxToken > idxPriorityToken[idx+1]):
                idx = idx + 2
                if idx == len(idxPriorityToken):
                    multiElem.append(origStr[(idxPreviousToken+1):idxToken])
                    if copyStr.rfind(token) < idxPriorityToken[idx-1]:
                        break
                    while (idxToken < idxPriorityToken[idx-1]):
                        copyStr = copyStr[:idxToken] + 'A' + copyStr[(idxToken+1):]
                        idxToken = copyStr.find(token)
                    leftStr = origStr[(idxToken + 1):]
                    elems = leftStr.split(token)
                    multiElem.extend(elems)
                    break
        else:
            multiElem.append(origStr[idxPriorityToken[idx]:(idxPriorityToken[idx+1]+1)])
            markLastIterPriorityToken = 1
            idx = idx + 2
            if idx == len(idxPriorityToken):
                if copyStr.rfind(token) < idxPriorityToken[idx-1]:
                    break
                while (idxToken < idxPriorityToken[idx-1]):
                    copyStr = copyStr[:idxToken] + 'A' + copyStr[(idxToken+1):]
                    idxToken = copyStr.find(token)
                leftStr = origStr[(idxToken + 1):]
                elems = leftStr.split(token)
                #multiElem = multiElem + elems
                multiElem.extend(elems)
                break
            else:
                idxToken = copyStr.find(token)
                while (idxToken < idxPriorityToken[idx-1]):
                    #copyStr[idxToken] = 'A'
                    copyStr = copyStr[:idxToken] + 'A' + copyStr[(idxToken+1):]
                    idxToken = copyStr.find(token)
    idxLastToken = origStr.rfind(token)
    idxLastPriorityToken = origStr.rfind(priorityToken)
    if (idxLastToken < idxLastPriorityToken):
        multiElem.append(origStr[(idxLastToken+1):])
    return multiElem


# //---  Read me  ---//
# Remove commented part starting with "//"
def removeDoubleSlash(str):
    idxToken = str.find("//")
    if (idxToken != -1):
        str = str[:idxToken]
###    the following if-sentence will remove commented part with /* and */ in the same line
#    idxToken = str.find("/*")
#    if (idxToken != -1):
#        idxToken_paired = str.find("*/")
#        print "Something is wrong in line: \n    " + str + \
#                "\n  /* is detected while */ is not"
#        raise SystemExit
#        str = str[:idxToken] + str[(idxToken_paired+2):]
    return str

    
# //---  Read me  ---//
# Remove commented part starting with sc
def removeSpecialComments(str, sc):
    idxToken = str.find(sc)
    if (idxToken != -1):
        str = str[:idxToken].strip()
    return str
    
# //---  Read me  ---//
# Return commented part starting with sc
def returnSpecialComments(str, sc):
    idxToken = str.find(sc)
    if (idxToken != -1):
        return str[(idxToken+len(sc)):].strip()
    return ''
    

# //---  Read me  ---//
# Removes all trailing whitespace of each string;
# the input variables strs should be a list of string variables.
def strip(strs):
    num = len(strs)
    newStrs = []
    for i in range(0, num):
        newStrs.append(strs[i].strip())
    return newStrs
   
def getFloatNumbers(strs):
    floatNum = []
    for str in strs:
        floatNum.append(float(str))
    return floatNum
 

def findValues(array, number):
    idxList = []
    for i in range(0, len(array)):
        if array[i] == number:
            idxList.append(i)
    return idxList
 

