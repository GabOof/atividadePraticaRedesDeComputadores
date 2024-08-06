from datetime import datetime
import socket
import threading


# Lista para armazenar as mensagens recebidas
mensagens = []


# Função que lida com a comunicação de um cliente
def handle_client(conexao, cliente):
    print(
        f"\n{'='*80}\nConectado por: {cliente} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    )

    while True:
        mensagem = conexao.recv(1024)  # Recebe a mensagem do cliente
        if not mensagem:
            break  # Se não houver mensagem, sai do loop

        mensagem = mensagem.decode("utf-8")  # Decodifica os bytes em string
        client_id, comando, *args = mensagem.split(
            " "
        )  # Separa o ID do cliente, comando e argumentos

        # Trata o comando SEND
        if comando == "SEND":
            destinatario = args[0]  # Primeiro argumento é o destinatário
            conteudo = " ".join(
                args[1:]
            )  # Junta o restante dos argumentos como conteúdo da mensagem
            mensagens.append(
                (destinatario, conteudo)
            )  # Adiciona a mensagem à lista de mensagens
            conexao.send(f"Mensagem enviada para {destinatario}".encode("utf-8"))

        # Trata o comando LIST
        elif comando == "LIST":
            remetente = args[0]  # Primeiro argumento é o ID do remetente
            msgs = [
                msg for destinatario, msg in mensagens if destinatario == remetente
            ]  # Filtra mensagens cujo destinatário é o remetente
            conexao.send(f"Mensagens: {msgs}".encode("utf-8"))

        # Trata comandos inválidos
        else:
            conexao.send("Comando inválido".encode("utf-8"))

        print(
            f"\nCliente {client_id} {cliente} executou opcão {comando} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        )

    # Fecha a conexão com o cliente
    conexao.close()
    print(
        f"\nConexão com cliente {client_id} {cliente} encerrada ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n{'='*80}"
    )


# Configurações do servidor
host = "127.0.0.1"  # Endereço IP do servidor (localhost)
porta = 5001  # Porta onde o servidor estará escutando
soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = (host, porta)
soquete.bind(origem)  # Vincula o socket ao endereço e porta especificados
soquete.listen(
    0
)  # Habilita o servidor a aceitar conexões (0 = número ilimitado de conexões pendentes)

print("\nServidor iniciado e aguardando conexões...")

# Loop para manter o servidor ativo e aceitando conexões
while True:
    conexao, cliente = soquete.accept()  # Aceita uma nova conexão
    client_thread = threading.Thread(
        target=handle_client, args=(conexao, cliente)
    )  # Cria uma nova thread para lidar com a conexão do cliente
    client_thread.start()  # Inicia a thread
