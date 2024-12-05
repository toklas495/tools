import sys

def craftPayload(chunk_size=20,payload=""):
    buffer = ""
    chunked = [payload[i:i+chunk_size] for i in range(0,len(payload),chunk_size)]
    for chunks in chunked:
        newChunk = chunks.replace('\n','').strip()
        length = hex(len(newChunk))[2:]
        buffer+=f"{length}\r\n{newChunk}\r\n"
    buffer+="0\r\n\r\n"
    return buffer


if __name__=="__main__":
    if len(sys.argv)>0:
        payload = sys.argv[1]
        size = int(sys.argv[2]) if len(sys.argv)==3 else 20
        chunked_payload = craftPayload(size,payload=payload)
        print(chunked_payload)
