from datetime import datetime
import socket
import threading


# Função que representa a tarefa de um cliente
def client_task(client_id):
    host = "127.0.0.1"  # Endereço IP do servidor (localhost)
    porta = 5001  # Porta onde o servidor estará escutando
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destino = (host, porta)

    try:
        soquete.connect(destino)
        mensagem = f"Olá Mundo! -> from client {client_id}"
        soquete.send(mensagem.encode("utf-8"))  # Envia a mensagem codificada em bytes
        print(
            f"{'='*80}\nCliente {client_id} enviou ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}): {mensagem}"
        )

    finally:
        soquete.close()
        print(
            f"\nCliente {client_id} fechou a conexão ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n{'='*80}"
        )


num_clients = 10

# Lista para armazenar as threads dos clientes
threads = []
for i in range(num_clients):
    t = threading.Thread(
        target=client_task, args=(i,)
    )  # Cria uma nova thread para cada cliente
    threads.append(t)
    t.start()

# Aguarda todas as threads de clientes finalizarem
for t in threads:
    t.join()

print("\nConexão concluída.")
