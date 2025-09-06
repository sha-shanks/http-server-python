import socket
import threading
import argparse
import os

# Used to parse the request data and extract required fields
def parse_request(request_data):
    header, body = request_data.split("\r\n\r\n")

    start_line = header.split("\r\n")[0]

    method, path, version = start_line.split(" ")

    headers = {}
    header_lines = header.split("\r\n")
    for line in header_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()

    return method, path, version, headers, body

def response(status, headers, body):
    """
    Returns a formatted HTTP response.

    args:
        status (str): HTTP status code and corresponding message
        headers (dict): A map of headers and their values.
        body (str): The body of the response.
    """
    return (status + "\r\n" + "".join(f"{key}: {value}\r\n" for key, value in headers.items()) + "\r\n" + body + "\r\n").encode("utf-8")


# to return the HTTP response for a GET method
def get_method(path, request_headers, request_body):
    status_codes = {
        200: "HTTP/1.1 200 OK",
        404: "HTTP/1.1 404 Not Found",
    }

    response_headers = {}
    response_body = ""

    if path == "/":
        status = status_codes[200]
    
    # Echo endpoint /echo/{str}
    elif path.lower().startswith("/echo/"):
        status = status_codes[200]
        response_body = path[6:]
        response_headers = {
            "Content-Type": "text/plain",
            "Content-Length": f"{len(response_body)}",
        }

    # User-Agent Endpoint /user-agent/
    elif path.lower() == "/user-agent" or path.lower() == "/user-agent/":
        status = status_codes[200]
        response_body = request_headers["user-agent"]
        response_headers = {
            "Content-Type": "text/plain",
            "Content-Length": f"{len(response_body)}",
        }
    
    # File sharing via HTTP
    elif path.lower().startswith("/files/"):
        file_name = path[7:].rstrip("/")

        try:
            with open(f"{source_directory}/{file_name}", 'r') as file:
                response_body = file.read()
            
            status = status_codes[200]
            response_headers = {
                "Content-Type": "application/octet-stream",
                "Content-Length": f"{len(response_body)}",
            }
        
        except FileNotFoundError:
            status = status_codes[404]

    # Default response if no match found    
    else:
        status = status_codes[404]

    return response(status, response_headers, response_body)

# HTTP response for POST method
def post_method(path, request_headers, request_body):
    status_codes = {
        201: "HTTP/1.1 201 Created",
        500: "HTTP/1.1 500 Internal Server Error"
    }
    response_headers = {}
    response_body = ""

    if path.lower().startswith("/files/"):
        file_name = path[7:].rstrip("/")

        try:
            with open(f"{source_directory}/{file_name}", 'a') as file:
                file.write(request_body[:int(request_headers["content-length"])])
            
            status = status_codes[201]
        
        except Exception as e:
            print(e)
            status = status_codes[500]

    return response(status, response_headers, response_body)

def handle_requests(client_socket):

    # Firstly we read the data received from the client connection socket
    data = client_socket.recv(1024)
    # print(f"Data received: {data.decode()}")

    request_data = data.decode()
    print(f"request_data: {request_data}")

    method, path, version, headers, body = parse_request(data.decode())

    if method == "GET":
        response = get_method(path, headers, body)

    elif method == "POST":
        response = post_method(path, headers, body)

    # To respond with 200 OK irrespective of the data received
    # response = "HTTP/1.1 200 OK\r\n\r\n"

    # Send the response to the client socket after encoding in urf-8 format
    client_socket.send(response)

    client_socket.close()


def main():
    # `argparser` library to take flags while running the program
    parser = argparse.ArgumentParser("HTTP Server From Scratch")
    parser.add_argument("-d", "--directory", help="Pass the directory to containing files accessible to the server.", required=False)
    args = parser.parse_args()

    global source_directory

    # Checking for directory flag and assigning the source directory
    if args.directory:
        source_directory = args.directory

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")
    print("Server is being started!")
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    # Server has started on the socket localhost:4221

    server_socket.listen()

    try:
        while 1:
            print("Waiting for a connection...")

            conn, addr = server_socket.accept() # wait for client

            print(f"Connection has been established with {addr}")

            # handle_requests(conn)
            threading.Thread(target=handle_requests, args=(conn,)).start()
    
    except KeyboardInterrupt:
        print("Server is shutting down...")
    
    finally:
        # Closing the server socket
        server_socket.close()

        print("Server has been shut down.")


if __name__ == "__main__":
    main()