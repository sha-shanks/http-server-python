import socket  # noqa: F401

# Used to parse the request data and extract required fields
def parse_request(request_data):
    header, body = request_data.split("\r\n\r\n")

    start_line = header.split("\r\n")[0]

    method, path, version = start_line.split(" ")

    return method, path, version

# to return the HTTP response for a given path
def get_response(path):

    # Map of paths to responses
    responses = {
        "/": "HTTP/1.1 200 OK\r\n\r\n",
    }

    default_response = "HTTP/1.1 404 Not Found\r\n\r\n"

    # Use the map or give a default response
    return responses.get(path, default_response)

def handle_requests(client_socket):

    # Firstly we read the data received from the client connection socket
    data = client_socket.recv(1024)
    # print(f"Data received: {data.decode()}")

    request_data = data.decode()

    method, path, version = parse_request(request_data)

    response = get_response(path)
    
    # To respond with 200 OK irrespective of the data received
    # response = "HTTP/1.1 200 OK\r\n\r\n"

    # Send the response to the client socket after encoding in urf-8 format
    client_socket.send(response.encode("utf-8"))

def main():
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

            handle_requests(conn)

            conn.close()
    
    except KeyboardInterrupt:
        print("Server is shutting down...")
    
    finally:
        # Closing the server socket
        server_socket.close()

        print("Server has been shut down.")


if __name__ == "__main__":
    main()