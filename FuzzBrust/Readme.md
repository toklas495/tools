![Uploading ChatGPT Image May 8, 2025, 12_37_11 PM.png…]()

# **FuzzBuster**

FuzzBuster is a tool that automates API fuzzing by sending fuzzed payloads to API endpoints. You can use this tool to test the security of API endpoints by identifying potential vulnerabilities. This tool supports sending requests simultaneously to multiple endpoints and fuzzing them using a wordlist.

## **Setup Instructions**

1. **Prepare Your Request File**  
   Create a request file containing HTTP requests that you want to fuzz. Each request should be separated by `@TOKLAS@`. If the request contains data (e.g., JSON, form data), ensure that the body is on a separate line. Here's an example of how to structure your request file:

   **Example request file (`requests.txt`)**:
   ```
   POST /api/login HTTP/1.1
   Host: example.com
   Content-Type: application/json
   
   {"username":"admin","password":"<FUZZ>"}
   @TOKLAS@
   
   GET /api/user/{user_id} HTTP/1.1
   Host: example.com
   Authorization: Bearer <TOKEN>
   @TOKLAS@
   ```

   In this example, the `<FUZZ>` placeholder will be replaced by the fuzz payloads during the fuzzing process.

2. **Prepare the Wordlist File**  
   Your wordlist file (`wordlist.txt`) should contain a list of fuzz payloads. Each fuzz payload will be used to replace the placeholders (e.g., `<FUZZ>`) in your request file.

   **Example wordlist file (`wordlist.txt`)**:
   ```
   admin
   test
   password
   <script>alert('XSS')</script>
   ```

3. **Run FuzzBuster**  
   To start the fuzzing process, simply run the following command:

   ```bash
   python fuzzbuster.py -w wordlist.txt
   ```

   - The `-w` option specifies the path to your wordlist file.
   - FuzzBuster will automatically read the request file, replace the placeholders with each fuzz payload from the wordlist, and send multiple requests simultaneously to the target endpoints.

## **How FuzzBuster Works**

1. FuzzBuster reads the request file and splits it at the `@TOKLAS@` separator.
2. It then parses each request, extracts the relevant headers and body data, and replaces the fuzz placeholders (e.g., `<FUZZ>`).
3. For each fuzz payload in the wordlist, FuzzBuster will send the request to the specified endpoint, fuzzing different parts of the request such as query parameters, headers, and body.
4. Fuzzing is done simultaneously by launching multiple threads to send requests concurrently, improving the speed and efficiency of the testing process.

## **Example Output**
The output will show the status of each fuzzed request along with the payload that was used. For example:

```
#- https://example.com/api/login HTTP/1.1 200 OK admin
#- https://example.com/api/login HTTP/1.1 200 OK test
#- https://example.com/api/login HTTP/1.1 500 Internal Server Error <script>alert('XSS')</script>
```

## **Running Multiple Requests Simultaneously**

FuzzBuster uses threading to send multiple requests concurrently. You can control the number of threads used for fuzzing by modifying the `THREAD_LIST` parameter in the code. This ensures faster fuzzing of endpoints and reduces the overall time required to complete the testing.


---

This section explains how to structure your request file with placeholders, how to run FuzzBuster with a wordlist, and how it performs simultaneous fuzzing. It also includes an example of how to structure the input and output for better understanding.
