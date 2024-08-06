from datetime import datetime
import socket


# Função para exibir o menu e capturar a escolha do usuário
def exibir_menu():
    print(f"\n{'='*80}\nEscolha uma ação:")
    print("1. Enviar mensagem")
    print("2. Listar mensagens")
    print(f"3. Sair\n{'='*80}\n")
    escolha = input("Digite o número da ação desejada:")
    return escolha


# Função para enviar uma mensagem
def enviar_mensagem(soquete, cliente_id):
    destinatario = input("\nDigite o ID do destinatário: ")
    conteudo = input("\nDigite a mensagem: ")
    mensagem = f"{client_id} SEND {destinatario} {conteudo}"  # Formata a mensagem com o ID do cliente, comando SEND, ID do destinatário e conteúdo da mensagem
    soquete.send(mensagem.encode("utf-8"))
    resposta = soquete.recv(1024).decode("utf-8")
    print(f"\nResposta do servidor: {resposta}")


# Função para listar mensagens
def listar_mensagens(soquete, cliente_id):
    mensagem = f"{client_id} LIST {cliente_id}"  # Formata a mensagem com o ID do cliente e o comando LIST
    soquete.send(mensagem.encode("utf-8"))
    resposta = soquete.recv(1024).decode("utf-8")
    print(f"\nMensagens recebidas: {resposta}")


# Função que representa a tarefa de um cliente
def client_task(client_id):
    host = "127.0.0.1"  # Endereço IP do servidor (localhost)
    porta = 5001  # Porta onde o servidor estará escutando
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destino = (host, porta)

    try:
        soquete.connect(destino)
        print(f"\nCliente {client_id} conectado ao servidor.")

        while True:
            escolha = exibir_menu()
            if escolha == "1":
                enviar_mensagem(soquete, client_id)
            elif escolha == "2":
                listar_mensagens(soquete, client_id)
            elif escolha == "3":
                print("\nFechando conexão...")
                break  # Sai do loop e fecha a conexão
            else:
                print("\nEscolha inválida. Tente novamente.")

    finally:
        soquete.close()
        print(
            f"\nCliente {client_id} fechou a conexão ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n{'='*80}"
        )


# Entrada do programa
if __name__ == "__main__":
    client_id = input("\nDigite o ID do cliente: ")
    client_task(client_id)  # Executa a tarefa do cliente com o ID fornecido
