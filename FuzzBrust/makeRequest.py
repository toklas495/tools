import os
import sys

def check():
    if os.path.exists('requests.txt'):
        return True
    else:
        print(f"\033[31m#File not found at {os.getcwd()} \033[0m")
        sys.exit(0)

def payloadReplacer(request,string="dump"):
    if request:
        return request.replace("FUZZ",string)
    else:
        sys.exit(0)


def openRequests():
    if check():
        tempStore = list()
        with open('requests.txt','r') as file:
            tempStore = file.read().split("@TOKLAS@")
            return tempStore
    else:
        sys.exit(0)

def requestParser(request,fuzz):
    if request:
        headerList = dict()
        fuzzyRequest = payloadReplacer(request,fuzz)
        HEADBODY = fuzzyRequest.split('\n\n')
        #********************************************#
        tempList = HEADBODY[0].split('\n')
        headerList["METHOD"],headerList["PATH"],_ = tempList[0].split()
        
        for metd in range(1,len(tempList)):
            key,value = tempList[metd].split(':',1)
            headerList[key.strip()] = value.strip()
        
        return headerList,HEADBODY[1] if len(HEADBODY)>1 else ""
    else:
        sys.exit(0)
            
        
        # tempStore contain a request




if __name__=="__main__":
    temp = openRequests()
    for i in temp:
        requestParser(i.strip(),"Yes ho gaya")