import threading
import socket
import os

host = '127.0.0.1'
puerto_inicio = 59000
puerto_fin = 59050
archivo_config = 'server_port.txt'

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def encontrar_puerto_libre(inicio, fin):
    """Encuentra un puerto libre en el rango especificado."""
    for puerto in range(inicio, fin + 1):
        try:
            servidor.bind((host, puerto))
            print(f'Servidor iniciado en el puerto {puerto}')
            # Escribir el puerto en el archivo de configuración
            with open(archivo_config, 'w') as archivo:
                archivo.write(str(puerto))
            return puerto
        except socket.error:
            continue
    raise Exception('No se encontraron puertos libres en el rango especificado.')

puerto = encontrar_puerto_libre(puerto_inicio, puerto_fin)
servidor.listen()

clientes = []
usuarios = []
cerrar_servidor = threading.Event()

def difundir(mensaje, remitente=None):
    """Envía el mensaje a todos los clientes conectados, excepto al remitente."""
    for cliente in clientes:
        if cliente != remitente:
            cliente.send(mensaje)

def eliminar_cliente(cliente, razon='ha salido del chat'):
    """Elimina al cliente de la lista y cierra la conexión."""
    if cliente in clientes:
        indice = clientes.index(cliente)
        nick = usuarios[indice]
        if razon == 'ha sido expulsado del chat':
            cliente.send('Has sido expulsado del chat'.encode('utf-8'))
        clientes.remove(cliente)
        cliente.close()
        usuarios.remove(nick)
        difundir(f'{nick} {razon}.'.encode('utf-8'))
        if razon == 'ha sido expulsado del chat':
            print(f'El usuario {nick} ha sido expulsado del chat.')

def manejar_cliente(cliente):
    """Maneja la comunicación con un cliente específico."""
    while not cerrar_servidor.is_set():
        try:
            mensaje = cliente.recv(1024)
            if mensaje:
                if mensaje.decode('utf-8').strip() == '/exit':
                    eliminar_cliente(cliente)
                    break
                difundir(mensaje, remitente=cliente)
            else:
                break
        except:
            eliminar_cliente(cliente, 'ha sido desconectado por error')
            break

def recibir():
    """Acepta nuevas conexiones y asigna alias a los clientes."""
    while not cerrar_servidor.is_set():
        try:
            print('El servidor está corriendo y escuchando...')
            cliente, direccion = servidor.accept()
            print(f'La conexión se ha establecido con {str(direccion)}')
            cliente.send('nick'.encode('utf-8'))
            nick = cliente.recv(1024).decode('utf-8')
            usuarios.append(nick)
            clientes.append(cliente)
            print(f'El nick de este cliente es {nick}')
            difundir(f'{nick} se ha conectado a la sala de chat'.encode('utf-8'))
            cliente.send('¡Te has conectado!'.encode('utf-8'))
            hilo = threading.Thread(target=manejar_cliente, args=(cliente,))
            hilo.start()
        except OSError:
            # El socket ha sido cerrado
            break

def comandos_admin():
    """Maneja los comandos del administrador."""
    while True:
        comando = input("")
        if comando.strip() == '/close':
            print('El servidor se está cerrando...')
            difundir('El servidor se está cerrando...'.encode('utf-8'))
            cerrar_servidor.set()  # Señal para cerrar el servidor y detener hilos
            servidor.close()
            for cliente in clientes:
                cliente.close()
            # Eliminar el archivo de configuración
            if os.path.exists(archivo_config):
                os.remove(archivo_config)
            break
        elif comando.startswith('/kick '): # Aún no hemos debuggeado para que elimine a usuarios con espacios en su nombre
            nick_a_expulsar = comando.split(' ')[1]
            if nick_a_expulsar in usuarios:
                indice = usuarios.index(nick_a_expulsar)
                cliente_a_expulsar = clientes[indice]
                eliminar_cliente(cliente_a_expulsar, 'ha sido expulsado del chat')
            else:
                print(f'No se encontró el usuario {nick_a_expulsar}')

if __name__ == "__main__":
    hilo_recibir = threading.Thread(target=recibir)
    hilo_recibir.start()
    comandos_admin()
