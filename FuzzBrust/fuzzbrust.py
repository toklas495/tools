import requests
import sys
import time
import threading
import queue
from urllib3.exceptions import InsecureRequestWarning
import warnings
import os
import json
import makeRequest as MR

# for hiding the proxy error 
warnings.simplefilter('ignore', InsecureRequestWarning) 

FUZZ_LIST = list() #FUZZ_LIST store our fuzzy payload

WORDLIST_PATH = ""



#  REQUEST file 
#*************************************
requestList = MR.openRequests()
REQUEST_FILE = queue.Queue()

for request in requestList:
    REQUEST_FILE.put(request)
#**************************************

# FUZZ filler which fill fuzz when my FUZZ_LIST is empty
#*********************************************************
def FUZZ_FILLER():
    path = WORDLIST_PATH
    if(os.path.exists(path)):
        with open(path,'r',encoding='utf-8') as file:
            WORDLIST = file.read().split('\n')
        for words in WORDLIST:
            FUZZ_LIST.append(words)
    else:
        sys.exit(1)

###################################################################################################

# Use proxy for sent result (response) on burpsuite 
# you can change proxy address as you wish.....
proxies = {
    'http':'http://127.0.0.1:8080',
    'https':'http://127.0.0.1:8080'
}

class Fuzzer:
    def __init__(self,request):
        self.HEADER = dict()
        self.REQUEST = request
        self.DATA = ""
        self.METHOD = ""
        self.URL = ""
        self.WORDLIST = queue.Queue()
        for fuzz in FUZZ_LIST:
            self.WORDLIST.put(fuzz)

    

    def fuzzer_Requests(self,FUZZ):

        try:
            session = requests.Session()
            request_manager = ""

            if self.DATA:
                if type(self.DATA)==dict:
                    request_manager = session.request(self.METHOD.lower(),self.URL,headers=self.HEADER,proxies=proxies,verify=False,json=self.DATA)
                elif type(self.DATA)==str:
                    request_manager = session.request(self.METHOD.lower(),self.URL,headers=self.HEADER,proxies=proxies,verify=False,data=self.DATA)
            else:
                request_manager = session.request(self.METHOD.lower(),self.URL,headers=self.HEADER,proxies=proxies,verify=False)


            if(request_manager.status_code==429):
                time.sleep(3)
                self.WORDLIST.put(FUZZ)
                

            print(f'\033[33m#-{self.URL:<60} {request_manager.status_code:<10} {FUZZ}\033[0m')

        except Exception as e:
            print("Exception -: %s" %e)

    
    def rateLimitBypass():
        pass



    def request_handle(self):
        while not self.WORDLIST.empty():
            payload = self.WORDLIST.get()
            if self.REQUEST:
                headers,data = MR.requestParser(self.REQUEST.strip(),payload)
                # ****************************************************************
                #   Feel the header method and assign url or method
                # ****************************************************************
                self.METHOD = headers["METHOD"]
                self.URL = f'https://{headers["Host"]}{headers["PATH"]}'
                for key in headers:
                    if key=="METHOD" or key=="PATH":
                        continue
                    self.HEADER[key] = headers[key]
                
                if data:
                    try:
                        self.DATA = json.loads(data)
                    except json.JSONDecodeError:
                        self.DATA = data
            
            self.fuzzer_Requests(payload)
                    

    def runner(self):
        THREAD_LIST = []
        for thr in range(10):
            thread = threading.Thread(target=self.request_handle)
            thread.start()
            THREAD_LIST.append(thread)
        for thr in THREAD_LIST:
            thr.join()

def mainWorker():
    #***************************************************#
    while not REQUEST_FILE.empty():
        request = REQUEST_FILE.get() 
        fuzzer = Fuzzer(request)
        fuzzer.runner()

def run():
    FUZZ_FILLER()
    THREAD_LIST = []
    for thr in range(2):
        thread = threading.Thread(target=mainWorker)
        thread.start()
        THREAD_LIST.append(thread)
    for thr in THREAD_LIST:
        thr.join()

def help():
    print('#[usage] python fuzzbrust.py --headers \'{"key":"value"}\' -w <wordlist>')
    sys.exit()

def parameterHandler(args):
    if len(args)>1:
        if "-w" in args:
            global WORDLIST_PATH
            WORDLIST_PATH = args[args.index("-w")+1]
        else:
            help()
    else:
        help()
       
if __name__=="__main__":
    args = sys.argv
    parameterHandler(args)
    run()
