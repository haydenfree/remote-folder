# Import socket module
import socket
import pickle
import time

def handle_connect(server_ip, server_port):
    global s 
    s = socket.socket()
    # connect to the server on local computer 
    s.connect((server_ip, int(server_port)))

def handle_upload(filename):
    # Open the file to be sent
    file = open(filename, "rb")
    fileData = file.read(1024)
    # Send the command to upload and the filename
    s.send(f"UPLOAD {filename}".encode())
    # Wait for server response
    s.recv(1024).decode()
    # Create variables for the initial start time and the total time elapsed
    initial_start = time.time()
    total_time_elapsed = 0
    # Create start time for measuring 1 second intervals, and buffers_sent
    start = time.time()
    buffers_sent = 0
    while fileData:
        # Send the current buffer
        s.send(fileData)
        # Increment the buffers sent
        buffers_sent = buffers_sent + 1
        # The time elapsed for the current 1 second window
        time_elapsed = time.time() - start
        # Update the total amount of time elapsed
        total_time_elapsed = time.time() - initial_start
        
        # Check if one second has passed
        if ( round(time_elapsed, 1) == 1.0 ):
            # Calculate amount of data transfered, in MB, for this second
            upload_speed = ((buffers_sent * 1024) / 1000000 ) / time_elapsed
            # Print the result to console
            print(f"Upload Speed: {upload_speed} MB/s")
            # Write the upload speed for the second to file for graphing
            with open('uploadspeed.csv', 'a') as upload_file:
                upload_file.write(f'{total_time_elapsed},{upload_speed}\n')
            # Redefine the start time as right now (a new one second window)
            start = time.time()
            # Reset the number of buffers sent to 0 (a new one second window)
            buffers_sent = 0
        
        # Read the next buffer of the file
        fileData = file.read(1024)
    s.close()

def handle_download(filename):
    # Send command to download file
    s.send(f"DOWNLOAD {filename}".encode())
    # receive confirmation
    confirmation = s.recv(1024).decode()
    if confirmation == "READY":
        buffers_received = 0
        file = open(filename, "wb")
        start = time.time()
        # Receive first buffer of the file
        fileData = s.recv(1024)
        while fileData:
            file.write(fileData)
            buffers_received = buffers_received + 1
            time_elapsed = time.time() - start
            download_speed = ((buffers_received * 1024) / 1000000 ) / time_elapsed
            if (buffers_received % 25000) == 0:
                print(f"Download Speed: {download_speed} MB/s")
                with open('downloadspeed.csv', 'a') as download_file:
                    download_file.write(f'{time_elapsed},{download_speed}\n')
            fileData = s.recv(1024)
        file.close()
        s.close()
    else:
        print(confirmation)

def handle_delete(filename):
    s.send(f"DELETE {filename}".encode())
    confirmation = s.recv(1024).decode()
    print(confirmation)
    s.close()

def handle_dir():
    s.send("DIR".encode())
    file_list = s.recv(1024)
    file_list = pickle.loads(file_list)
    for file in file_list:
        print(f"{file[0]}, {file[1]}, {file[2]}")
    s.close()

def main():
    while True:
        user_input = input("$ ")
        user_input = user_input.split()
        command = user_input[0]
        args = user_input[1:]

        if command == "exit":
            break
        elif command == "CONNECT":
            # Handle the CONNECT command
            handle_connect(args[0], args[1])
        elif command == "UPLOAD":
            handle_upload(args[0])
        elif command == "DOWNLOAD":
            handle_download(args[0])
        elif command == "DELETE":
            handle_delete(args[0])
        elif command == "DIR":
            handle_dir()
        else:
            pass

if '__main__' == __name__:
    main()