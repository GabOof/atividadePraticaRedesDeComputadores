import socket

host = "127.0.0.1" # Endereco IP do Servidor
porta = 5000 # Porta que o Servidor esta
soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
destino = (host, porta)
soquete.connect(destino)
soquete.send("Olá Mundo!")
soquete.close()
