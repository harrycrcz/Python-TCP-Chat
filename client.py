import threading
import socket
import time
import os

nick = input('Escoge un nick: ')
archivo_config = 'server_port.txt'

def obtener_puerto_servidor():
    """Lee el puerto del archivo de configuración."""
    while not os.path.exists(archivo_config):
        print('Esperando a que el servidor esté disponible...')
        time.sleep(1)
    with open(archivo_config, 'r') as archivo:
        puerto = int(archivo.read().strip())
    return puerto

puerto = obtener_puerto_servidor()
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(('127.0.0.1', puerto))

def recibir_cliente():
    """Recibe mensajes del servidor y los muestra en la consola."""
    while True:
        try:
            mensaje = cliente.recv(1024).decode('utf-8')
            if mensaje == 'nick':
                cliente.send(nick.encode('utf-8'))
            else:
                print(mensaje)
        except:
            break

def enviar_cliente():
    """Envía mensajes al servidor."""
    while True:
        mensaje = input("")
        if mensaje.strip() == '/exit':
            cliente.send('/exit'.encode('utf-8'))
            cliente.close()
            break
        else:
            cliente.send(f'{nick}: {mensaje}'.encode('utf-8'))

hilo_recibir = threading.Thread(target=recibir_cliente)
hilo_recibir.start()

hilo_enviar = threading.Thread(target=enviar_cliente)
hilo_enviar.start()
