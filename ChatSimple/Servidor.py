import socket
import threading
import time

MAX_PP = 100
PORT = 5000
terminate = False
listPP = []
listThreads = []
mtxList = threading.Lock()
mtxScrn = threading.Lock()

class people:
    shared_variable = 0
    def __init__(self, conn: socket.socket, dir):
        self._conn = conn
        self._dir = dir
        self._name = people.shared_variable
        people.shared_variable+=1
    def getConn(self) -> socket.socket:
        return self._conn
    def getName(self):
        return self._name

def createThreads(pp : people):
    global listThreads
    threadManageClients = threading.Thread(target=manageClients, args=(pp,), name="Thread_Manage_Clients")
    threadManageClients.start()
    listThreads.append(threadManageClients)

def joinThreads():
    global listThreads 
    for thread in listThreads:
        thread.join()

def isClientAlive(client_socket):
    try:
        client_socket.send(b'\x00') 
        return True
    except socket.error:
        return False

def manageClients(clt : people):
    conn = clt.getConn()
    while isClientAlive(conn):
        try:
            msg = conn.recv(1024).decode("ascii")
            with mtxScrn:  # Use with for lock acquisition and release
                print(clt._name ," > ", msg)
        except:
            pass
    conn.close()
    with mtxList:
        listPP.remove(clt)
                   
def connection(port, max_pend) -> socket.socket:
    ss = socket.socket()
    try:
        ss.bind(("127.0.0.1", port))
        ss.listen(max_pend)
    except Exception as e:
        ValueError(e)
    return ss

def receiveClients(ss: socket.socket):
    global listPP, terminate 
    while not terminate:
        try:
            ss.settimeout(1.0)  # Timeout to check terminate
            conn, dir = ss.accept()
            pp = people(conn, dir)
            with mtxList:  # Use with for lock acquisition and release
                listPP.append(pp)
            createThreads(pp)
        except socket.timeout:
            continue  # If accept times out, loop to check 'terminate'
        except Exception as e:
            print(f"Error handling client connection: {e}")

ss = connection(PORT,MAX_PP)
threadReiveClients = threading.Thread(target=receiveClients, args=(ss,), name="Thread_Receive_Clients")
threadReiveClients.start()

time.sleep(30)
while True:
    with mtxList:
        if len(listPP) == 0:
            terminate = True
            break

threadReiveClients.join()
joinThreads()
ss.close()