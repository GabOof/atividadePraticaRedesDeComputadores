from datetime import datetime
import socket


# Função para exibir o menu e capturar a escolha do usuário
def exibir_menu():
    print(f"\n{'='*80}\nEscolha uma ação:")
    print("1. Enviar mensagem")
    print("2. Listar mensagens")
    print(f"3. Sair\n{'='*80}\n")
    escolha = input(
        "Digite o número da ação desejada: "
    )  # Captura a escolha do usuário
    return escolha


# Função para enviar uma mensagem
def enviar_mensagem(soquete, cliente_id):
    destinatario = input(
        "\nDigite o ID do destinatário: "
    )  # Captura o ID do destinatário
    conteudo = input("\nDigite a mensagem: ")  # Captura o conteúdo da mensagem
    mensagem = f"{cliente_id} SEND {destinatario} {conteudo}"  # Formata a mensagem com o ID do cliente, comando SEND, ID do destinatário e conteúdo
    soquete.send(
        mensagem.encode("utf-8")
    )  # Envia a mensagem codificada para o servidor
    resposta = soquete.recv(1024).decode(
        "utf-8"
    )  # Recebe a resposta do servidor e decodifica
    print(f"\nResposta do servidor: {resposta}")  # Exibe a resposta recebida


# Função para listar mensagens
def listar_mensagens(soquete, cliente_id):
    mensagem = f"{cliente_id} LIST {cliente_id}"  # Formata a mensagem com o ID do cliente e o comando LIST
    soquete.send(
        mensagem.encode("utf-8")
    )  # Envia a mensagem codificada para o servidor
    resposta = soquete.recv(1024).decode(
        "utf-8"
    )  # Recebe a resposta do servidor e decodifica
    print(f"\nMensagens recebidas: {resposta}")  # Exibe as mensagens recebidas


# Função que representa a tarefa de um cliente
def client_task(cliente_id):
    host = "127.0.0.1"  # Endereço IP do servidor (localhost)
    porta = 5001  # Porta onde o servidor estará escutando
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP/IP
    destino = (host, porta)

    try:
        soquete.connect(destino)  # Conecta ao servidor
        print(f"\nCliente {cliente_id} conectado ao servidor.")

        while True:
            escolha = exibir_menu()  # Exibe o menu e captura a escolha do usuário
            if escolha == "1":
                enviar_mensagem(soquete, cliente_id)  # Envia uma mensagem
            elif escolha == "2":
                listar_mensagens(soquete, cliente_id)  # Lista mensagens
            elif escolha == "3":
                print("\nFechando conexão...")
                break  # Sai do loop e encerra a conexão
            else:
                print(
                    "\nEscolha inválida. Tente novamente."
                )  # Mensagem para escolha inválida

    finally:
        soquete.close()  # Fecha a conexão com o servidor
        print(
            f"\nCliente {cliente_id} fechou a conexão ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n{'='*80}"
        )


# Entrada do programa
if __name__ == "__main__":
    cliente_id = input("\nDigite o ID do cliente: ")  # Captura o ID do cliente
    client_task(cliente_id)  # Executa a tarefa do cliente com o ID fornecido
