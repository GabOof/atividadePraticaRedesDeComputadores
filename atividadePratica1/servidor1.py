from datetime import datetime
import socket
import threading


# Função que lida com a comunicação de um cliente
def handle_client(conexao, cliente):
    print(
        f"\n{'='*80}\nConectado por: {cliente} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    )
    while True:
        mensagem = conexao.recv(1024)
        if not mensagem:
            break  # Se não houver mensagem, sai do loop
        print(
            f"\nMensagem recebida de {cliente} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}): {mensagem.decode('utf-8')}"
        )

    conexao.close()
    print(
        f"\nConexão com {cliente} encerrada ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n{'='*80}"
    )


host = "127.0.0.1"  # Endereço IP do servidor (localhost)
porta = 5001  # Porta onde o servidor estará escutando
soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = (host, porta)
soquete.bind(origem)
soquete.listen(0)

print("\nServidor iniciado e aguardando conexões...")

# Loop para manter o servidor ativo e aceitando conexões
while True:
    conexao, cliente = soquete.accept()
    client_thread = threading.Thread(
        target=handle_client, args=(conexao, cliente)
    )  # Cria uma nova thread para lidar com a conexão do cliente
    client_thread.start()
