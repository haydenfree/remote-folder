import socket
import os
import datetime
import pickle

HOST = 'localhost'
PORT = 12345


def handle_upload(filename):
    file = open(filename, "wb")
    conn.send("READY".encode())
    fileData = conn.recv(1024)
    while fileData:
        file.write(fileData)
        fileData = conn.recv(1024)
    file.close()
    print("File upload complete.")


def handle_download(filename):
    try:
        file = open(filename, "rb")
    except OSError:
        conn.send(f"ERROR: Could not open/read/find {filename}".encode())
        return
    with file:
        conn.send("READY".encode())
        fileData = file.read(1024)
        while fileData:
            # Start sending the file
            conn.send(fileData)
            fileData = file.read(1024)
        file.close()
        conn.close()
        print("File sent to client.")


def handle_delete(filename):
    if os.path.exists(filename):
        os.remove(filename)
        conn.send(f"Deleted {filename}".encode())

def handle_dir():
    files = []
    for f in os.listdir('.'):
        if os.path.isfile(f):
            files.append([f, f"{os.path.getsize(f)} bytes", datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%A, %B %d, %Y %I:%M:%S")])
    data = pickle.dumps(files)
    conn.send(data)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
print("socket binded to %s" % (PORT))

while True:
    # put the socket into listening mode
    s.listen()
    print("socket is listening")

    # Establish connection with client.
    conn, addr = s.accept()
    print('Received connection from', addr)

    while True:
        data = conn.recv(1024).decode().split()
        if not data:
            break
        elif data[0] == "UPLOAD":
            handle_upload(data[1])
        elif data[0] == "DOWNLOAD":
            handle_download(data[1])
            break
        elif data[0] == "DELETE":
            handle_delete(data[1])
            pass
        elif data[0] == "DIR":
            handle_dir()
