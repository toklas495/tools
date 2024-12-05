import socket
import re
import os
import sys
import ssl



def importFile(path):
    """Read the file and return its contents as a list of lines."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{path}' does not exist.")
    with open(path, 'r') as file:
        return ((file.read()).strip()).split('\n')


def makeChunkedData(path):
    """Parse the request file and extract Host and the HTTP request."""
    chunkedData = importFile(path)
    host_line = next((line for line in chunkedData if line.startswith("Host:")), None)
    if not host_line:
        raise ValueError("No 'Host' header found in the request file.")
    
    Host = re.findall(r"Host: ?([^ ]+)", host_line.strip())[0]
    buffer = ""
    for methods in chunkedData:
        if(methods==""):
            buffer+="\r\n"
        else:
            buffer+=f'{methods}\r\n'
    buffer+="\r\n"
    return buffer, Host


def sendRequest(path, port):
    """Send the HTTP/HTTPS request and print the response."""
    request, HOST = makeChunkedData(path)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if port == 443:
        client = ssl.create_default_context().wrap_socket(client, server_hostname=HOST)
    
    try:
        client.connect((HOST, port))
        client.sendall(request.encode())
        response = b""
        while True:
            buffer = client.recv(4096)
            if not buffer:
                break
            response += buffer
        print(f'\033[36mHOST:->{HOST}:\033[0m')
        print(f'\033[32mRESPONSE:->\033[0m\r\n\r\n\033[93m{response.decode()}\033[0m')
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()



if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1] 
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 443
        sendRequest(file_path, port)
    else:
        print("Usage: python socky.py <request_file> [port]")
