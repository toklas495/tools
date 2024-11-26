import requests
import sys
import time
import threading
import queue
from urllib3.exceptions import InsecureRequestWarning
import warnings
import os
import random
import json

# for hiding the proxy error 
warnings.simplefilter('ignore', InsecureRequestWarning) 

FUZZ_LIST = list() #FUZZ_LIST store our fuzzy payload

HEADERS = {"HEADER":"","WORDLIST":""}



#  REQUEST file 
with open('requests.json','r') as file:
        json_file = json.load(file)
REQUEST_FILE = queue.Queue()

for request in json_file:
    REQUEST_FILE.put(request)



# with open('wordlist/requests.json','r') as file:
#     DATA = json.load(file)
# DATA Store the JSON file 

def process_word(word):
#    try:
#        return int(word)
#    except ValueError:
#        pass
#    try:
#        return float(word)
#    except ValueError:
#        pass
#   try:
#        return json.loads(word)
#    except json.JSONDecodeError:
#        pass
    return word

# FUZZ filler which fill fuzz when my FUZZ_LIST is empty

def FUZZ_FILLER():
    path = HEADERS["WORDLIST"]
    if(os.path.exists(path)):
        with open(path,'r',encoding='utf-8') as file:
            WORDLIST = file.read().split('\n')
        for words in WORDLIST:
            FUZZ_LIST.append(process_word(words))
    else:
        sys.exit(1)



###################################################################################################

# this algorithm replace the FUZZ with your FUZZ Payload

def replace_fuzz(data, payload):
    # Base case: if the data is a string and matches 'fuzz', return the payload
    if isinstance(data, str):
        if 'FUZZ' in data:
            return data.replace('FUZZ',payload)
        else:
            return data
    
    
    # If the data is a dictionary, recurse over each key and value
    elif isinstance(data, dict):
        return {key: replace_fuzz(value, payload) for key, value in data.items()}
    
    # If the data is a list, recurse over each element in the list
    elif isinstance(data, list):
        return [replace_fuzz(item, payload) for item in data]
    
    # If the data is a boolean, int, or any other primitive type, return it as is
    else:
        return data




proxies = {
    'http':'http://127.0.0.1:8080',
    'https':'http://127.0.0.1:8080'
}


#Request Counter


class Fuzzer:
    def __init__(self,METHOD,TARGET_URL,DATA=""):
        self.METHOD=METHOD # Method 
        self.URL=TARGET_URL # Target URL
        self.DATA=DATA # DATA
        self.headers = HEADERS["HEADER"] # headers parameters
        self.WORDLIST = queue.Queue()
        for fuzz in FUZZ_LIST:
            self.WORDLIST.put(fuzz)

    

    def fuzzer_Requests(self,fuzz_data,FUZZ):

        try:
            session = requests.Session()
            request_manager = ""
            if(self.METHOD=="POST"):
                request_manager = session.post(self.URL,headers=self.headers,proxies=proxies,verify=False,json=fuzz_data)
            elif(self.METHOD=="GET"):
                request_manager = session.get(fuzz_data,headers=self.headers,proxies=proxies,verify=False)
            else:
                request_manager = session.put(self.URL,headers=self.headers,proxies=proxies,verify=False,json=fuzz_data)

            if(request_manager.status_code==429):
                time.sleep(3)
                self.WORDLIST.put(FUZZ)
                

            print(f'#-{self.URL:<60} {request_manager.status_code:<10} {FUZZ}')

        except Exception as e:
            print("Exception -: %s" %e)



    def request_handle(self):
        while not self.WORDLIST.empty():
            payload = self.WORDLIST.get()
            if self.DATA:
                fuzz_data = replace_fuzz(self.DATA,payload)
            else:
                fuzz_data = replace_fuzz(self.URL,payload)
            self.fuzzer_Requests(fuzz_data,payload)


    def runner(self):
        THREAD_LIST = []
        for thr in range(10):
            thread = threading.Thread(target=self.request_handle)
            thread.start()
            THREAD_LIST.append(thread)
        for thr in THREAD_LIST:
            thr.join()

def helper():
    ####################################################

    while not REQUEST_FILE.empty():
        request = REQUEST_FILE.get()        
        METHOD = request['METHOD']
        TARGET_URL = request['URL']
        print(f'\nURL:-{TARGET_URL}\n')
        DATA = request['DATA']
        TARGET_REQUEST = Fuzzer(METHOD,TARGET_URL,DATA)
        TARGET_REQUEST.runner()

def run():
    FUZZ_FILLER()
    THREAD_LIST = []
    for thr in range(2):
        thread = threading.Thread(target=helper)
        thread.start()
        THREAD_LIST.append(thread)
    for thr in THREAD_LIST:
        thr.join()

def help():
    print('#[usage] python fuzzbrust.py --headers \'{"key":"value"}\' -w <wordlist>')
    sys.exit()

def parameterHandler(args):
    if len(args)>1:
        if "--headers" in args:
            HEADERS["HEADER"] = json.loads(args[args.index("--headers")+1])
        else:
            help()
        
        if "-w" in args:
            HEADERS["WORDLIST"] = args[args.index("-w")+1]
        else:
            help()
    else:
        help()
       
if __name__=="__main__":
    args = sys.argv
    parameterHandler(args)
    run()
