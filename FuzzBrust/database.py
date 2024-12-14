import sqlite3
import random
import json
import re

def create_tables():
    try:
        """Creates the necessary tables in the SQLite database."""
        database = f'responses_{random.randint(100000000,999999999)}.db'
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        # Table for URLs and unique IDs
        cursor.execute('''
        CREATE TABLE hashes (
        hash_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash_value TEXT UNIQUE NOT NULL             
        ); 
        ''')

        # Table for status codes and their headers + responses
        cursor.execute('''
        CREATE TABLE requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,  
        hash_id INTEGER,   
        url TEXT NOT NULL,                           
        method TEXT NOT NULL,
        status_code INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hash_id) REFERENCES hashes(hash_id)  
        );
        ''')

        cursor.execute('''
        CREATE TABLE fuzzing_responses (
        response_id INTEGER PRIMARY KEY AUTOINCREMENT,  
        request_id INTEGER,                             
        fuzz_payload TEXT NOT NULL,
        response_status_code INTEGER NOT NULL,
        response_header TEXT NOT NULL,
        response_data TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (request_id) REFERENCES requests(request_id)
        );
        ''')
        connection.commit()
        connection.close()
    except Exception as error:
        print(f"Exception as e: {error}")

    return database


def filter_dynamic_fields(storedData, headers, data, ignore_fields):
    """
    Check if a given response (headers + data) is unique compared to stored responses.
    """
    # Iterate over stored responses
    for row in storedData:
        # Parse stored JSON headers and stored data
        stored_resp = json.loads(row[0])  # Parse headers as JSON
        stored_data = row[1]  # Stored data string

        # Step 1: Compare headers (ignoring specified fields)
        headers_match = all(
            key in stored_resp and stored_resp[key] == value
            for key, value in headers.items()
            if key not in ignore_fields
        )

        # If headers don't match, continue to the next stored response
        if not headers_match:
            continue

        # Step 2: If headers match, compare data with Jaccard similarity
        if data:
            threshold_frequency = 0.77  # Adjust as needed
            
            # Split data and stored data into tokens
            split_data = set(re.split(r'[\n:, ]', data))
            split_stored_data = set(re.split(r'[\n:, ]', stored_data))

            # Calculate Jaccard similarity
            intersection = split_data & split_stored_data
            union = split_data | split_stored_data
            jaccard_similarity = len(intersection) / len(union)
            # If similarity exceeds the threshold, consider it not unique
            
            if jaccard_similarity > threshold_frequency:
                return False  # Duplicate found
            

        # If headers match but no data is provided, assume it's not unique
        elif not data:
            return False

    # If no match is found after checking all stored responses, it's unique
    return True


def store(database,method,hash,response,fuzz_payload,ignore_fields):
    """Stores the response in the database if it's unique."""
    try:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        response_url = response.url
        response_status_code = response.status_code
        response_headers = dict(response.headers)
        response_data  = str(response.text)
        response_method = method
    except Exception as error:
        print("Error: {error}")

     # Check if the URL is already in the database
    is_unique = False
    hash_id = ""
    try:
        cursor.execute('SELECT hash_id FROM hashes WHERE hash_value=?', (hash,))
        url_row = cursor.fetchone()

        if url_row is None:
        # Insert the new URL and get its ID
            cursor.execute('INSERT INTO hashes (hash_value) VALUES (?)', (hash,))
            connection.commit()
            hash_id = cursor.lastrowid
        else:
            hash_id = url_row[0]
    
    # Check if the status code is new for this URL
        cursor.execute('SELECT 1 FROM requests WHERE hash_id = ? AND status_code = ? AND method=? AND url=?', (hash_id, response_status_code,response_method,response_url))
        status_row = cursor.fetchone()
        requests_id = ""
        if status_row is None:
            # Insert the new status code
            cursor.execute('INSERT INTO requests (hash_id,url,method,status_code) VALUES (?, ?,?,?)', (hash_id,response_url,response_method,response_status_code))
            connection.commit()
            requests_id = cursor.lastrowid
            is_unique = True
    except Exception as e:
        print(f"Error as e {e}")

    try:
        if is_unique:
             # If status code is unique, store headers and body
            cursor.execute('INSERT INTO fuzzing_responses (request_id, fuzz_payload, response_status_code, response_header,response_data) VALUES (?, ?,?, ?, ?)',
                           (requests_id,fuzz_payload, response_status_code,json.dumps(response_headers), response_data))
            connection.commit()
            print(f"Stored unique response for URL: {hash_id} with status code: {response_status_code}")
        else:
             # Check if the headers and body are unique
            cursor.execute("SELECT request_id FROM requests WHERE hash_id=? AND method=? AND status_code=? AND url=?",(hash_id,response_method,response_status_code,response_url))
            reqeusts_id = cursor.fetchone()[0]
            cursor.execute("""SELECT fr.response_header, fr.response_data
                            FROM fuzzing_responses AS fr
                            JOIN requests AS re ON re.request_id = fr.request_id
                            WHERE re.hash_id = ?;""",(hash_id,))
            existing_row = cursor.fetchall()
            if (filter_dynamic_fields(existing_row,response_headers,response_data,ignore_fields)):
                cursor.execute('''INSERT INTO fuzzing_responses
                (request_id,fuzz_payload,response_status_code,response_header,response_data) 
                VALUES(?,?,?,?,?)''',(reqeusts_id,fuzz_payload,response_status_code,json.dumps(response_headers),response_data))
                connection.commit()
    except Exception as error:
        print(f"Exception as Errro: {error}")
    connection.close()            


if __name__=="__main__":
    pass
