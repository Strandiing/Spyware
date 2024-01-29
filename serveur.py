import threading
import socket
import time
import sys

def handle_co():
    global running_thrd
    global client_sockets
    while running_thrd:
        try:
            client, addr = server.accept()
            client_sockets.append(client)
            rcvFile = threading.Thread(target=recvFileFrmKlg, args=(client,))
            rcvFile.start()       
        except BlockingIOError:
            continue

def recvFileFrmKlg(client_sock):
    global running_thrd
    file_status = False
    try:
        while running_thrd:
            file_name = client_sock.recv(1024) #Recoit le nom du fichier
            if not file_name:
                print("Aucune donnée reçu, fin de la connexion")
                break
            file_name = file_name.decode().split('\n')[0]
            with open(file_name, "wb") as file:#file = open(file_name, "wb")
                print("recv debut")
                file_bytes = b"" 
                while running_thrd:
                    data = client_sock.recv(1024) #Va recevoir les bytes du fichier du client
                    file_bytes += data    
                    if b"<END>" in file_bytes: #Si il rencontre la chaine de caractère "<END>" il arrête d'écrire
                        file_bytes = file_bytes[:-5]
                        file_status = True
                        break
                    
                file.write(file_bytes)
                file.flush()

                if file_status:                       
                    client_sock.sendall(b"ACK")    
                    print("recv fin")
    except KeyboardInterrupt:
        file.close()
        client_sock.close()
        print("Connexion fermée")        

if __name__ == '__main__' :
    host, port = ("localhost", 9998)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET = IPv4, SOCK_STREAM = TCP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port)) #Assigne l'IP au port
    server.listen() #Prépare le socket à accepter des connections
    #client, addr = server.accept() #Pour accepter une connexion d'un client TCP
    server.setblocking(True)

    running_thrd = True
    client_sockets = []

    thrd_co = threading.Thread(target=handle_co)
    thrd_co.start()

    try:
        while running_thrd:
            time.sleep(1)
    except KeyboardInterrupt:
        print("CTRL + C detected")
        running_thrd = False
        for client in client_sockets:
            try:
                client.sendall(b"<SERVER_SHUTDOWN>")
            except:
                pass
        server.close()
        thrd_co.join()
        print("Le serveur va s'éteindre")
        sys.exit()